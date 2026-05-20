"""
诈骗软件识别核心模块（硅基流动 API 版）
功能：分析软件截图，判断是否为诈骗软件
使用硅基流动 API 调用 Qwen/Qwen3.6-35B-A3B 模型
"""

import os
import base64
import re
from openai import OpenAI


class ScamDetector:
    """诈骗软件检测器（硅基流动 API 版）"""

    def __init__(self, api_key=None, model="Qwen/Qwen3.6-35B-A3B"):
        """
        初始化检测器

        Args:
            api_key: 硅基流动 API 密钥
            model: 使用的模型，默认 Qwen/Qwen3.6-35B-A3B
        """
        self.api_key = api_key or "sk-rlhukdtkuezyammgapsqzcakpopmcblzkkjxoidujermxknp"
        self.model = model
        self.base_url = "https://api.siliconflow.cn/v1"
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

        self.system_prompt = """你是一个专业的反诈骗安全分析师。你的任务是分析用户提供的软件截图，判断该软件是否可能是诈骗软件。

请按照以下结构进行详细分析：

1. 界面内容识别：
   - 识别界面中的所有文字内容（按钮、标题、提示文字等）
   - 识别界面布局特征（是否模仿官方App、UI风格等）
   - 识别任何标识、水印或Logo

2. 风险要素识别：
   - 高收益宣传话术识别（如"日赚千元"、"稳赚不赔"等）
   - 诱导性按钮识别（如"立即充值"、"抢先体验"等）
   - 敏感操作提示（如转账、输入密码、提供个人信息等）
   - 仿冒特征识别（模仿银行、证券、政府机构界面等）

3. 风险评估：
   - 诈骗可能性：0-100%（给出具体数值）
   - 诈骗类型：骗钱/涉黄/赌博/传销/仿冒/钓鱼/其他（明确选择）
   - 风险等级：安全/低风险/中风险/高风险/极高风险（具体选择，不要"未知"）

4. 详细分析说明：
   - 列出所有识别到的可疑点
   - 说明每个可疑点的风险原因
   - 提供具体的判断依据

5. 安全建议：
   - 针对识别到的风险给出具体建议
   - 告知用户应采取的措施

请用中文清晰、详细地回答，格式清晰，让普通民众也能看懂。"""

    def encode_image(self, image_path):
        """将图片编码为 Base64"""
        try:
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到图片文件: {image_path}")
        except Exception as e:
            raise Exception(f"图片编码失败: {e}")

    def _clean_markdown_format(self, text):
        """清理文本中的 Markdown 格式，移除 **xxx** 等格式标记"""
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*(?!\*)', '', text)
        return text

    def analyze_screenshot(self, image_path, user_description=None):
        """
        分析软件截图

        Args:
            image_path: 截图文件路径
            user_description: 用户对软件的描述（可选）

        Returns:
            dict: 包含分析结果的字典
        """
        base64_image = self.encode_image(image_path)

        user_query = "请对该软件截图进行深度语义分析，判断是否为诈骗软件。"
        if user_description:
            user_query += f"\n\n用户描述：{user_description}"

        user_query += "\n\n请严格按照以下格式输出结果，不要使用任何Markdown格式（如**加粗**等）：\n\n" \
                     "【一、界面内容识别】\n" \
                     "1. 界面顶部内容：[描述界面顶部的文字和布局]\n" \
                     "2. 界面主体内容：[描述界面主体区域]\n" \
                     "3. 界面底部内容：[描述界面底部区域]\n" \
                     "4. 其他特殊元素：[描述其他需要注意的元素]\n\n" \
                     "【二、风险要素识别】\n" \
                     "1. 高收益话术：[列出识别到的相关文字]\n" \
                     "2. 诱导性按钮：[列出识别到的按钮]\n" \
                     "3. 敏感操作：[列出识别到的敏感操作]\n" \
                     "4. 仿冒特征：[描述是否存在仿冒特征]\n\n" \
                     "【三、风险评估】\n" \
                     "1. 诈骗可能性：[0-100%]\n" \
                     "2. 诈骗类型：[骗钱/涉黄/赌博/传销/仿冒/钓鱼/其他]\n" \
                     "3. 风险等级：[安全/低风险/中风险/高风险/极高风险]\n\n" \
                     "【四、详细分析说明】\n" \
                     "[详细说明识别到的可疑点及判断依据]\n\n" \
                     "【五、安全建议】\n" \
                     "[针对识别结果给出具体安全建议]"

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                        {"type": "text", "text": user_query}
                    ]
                }
            ],
            max_tokens=6000,
            temperature=0.3
        )

        result = response.choices[0].message.content
        result = self._clean_markdown_format(result)
        return {
            "success": True,
            "result": result,
            "image_path": image_path
        }

    def analyze_screenshots(self, image_paths, user_description=None):
        """
        分析多张软件截图（最多5张）

        Args:
            image_paths: 截图文件路径列表
            user_description: 用户对软件的描述（可选）

        Returns:
            dict: 包含分析结果的字典
        """
        # 限制最多5张图片
        image_paths = image_paths[:5]
        
        # 编码所有图片
        base64_images = [self.encode_image(path) for path in image_paths]

        user_query = f"请对这{len(image_paths)}张软件截图进行深度语义分析，综合判断是否为诈骗软件。"
        if user_description:
            user_query += f"\n\n用户描述：{user_description}"

        user_query += "\n\n请严格按照以下格式输出结果，不要使用任何Markdown格式（如**加粗**等）：\n\n" \
                     "【一、界面内容识别】\n" \
                     "1. 界面顶部内容：[描述界面顶部的文字和布局]\n" \
                     "2. 界面主体内容：[描述界面主体区域]\n" \
                     "3. 界面底部内容：[描述界面底部区域]\n" \
                     "4. 其他特殊元素：[描述其他需要注意的元素]\n\n" \
                     "【二、风险要素识别】\n" \
                     "1. 高收益话术：[列出识别到的相关文字]\n" \
                     "2. 诱导性按钮：[列出识别到的按钮]\n" \
                     "3. 敏感操作：[列出识别到的敏感操作]\n" \
                     "4. 仿冒特征：[描述是否存在仿冒特征]\n\n" \
                     "【三、风险评估】\n" \
                     "1. 诈骗可能性：[0-100%]\n" \
                     "2. 诈骗类型：[骗钱/涉黄/赌博/传销/仿冒/钓鱼/其他]\n" \
                     "3. 风险等级：[安全/低风险/中风险/高风险/极高风险]\n\n" \
                     "【四、详细分析说明】\n" \
                     "[详细说明识别到的可疑点及判断依据]\n\n" \
                     "【五、安全建议】\n" \
                     "[针对识别结果给出具体安全建议]"

        # 构建包含多张图片的消息内容
        content = []
        for i, base64_image in enumerate(base64_images):
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}})
        content.append({"type": "text", "text": user_query})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": content
                }
            ],
            max_tokens=2000,
            temperature=0.3
        )

        result = response.choices[0].message.content
        result = self._clean_markdown_format(result)
        return {
            "success": True,
            "result": result,
            "image_paths": image_paths
        }


def analyze_scam(image_path, api_key=None, user_desc=None):
    """
    便捷函数：分析截图是否为诈骗软件

    Args:
        image_path: 截图路径
        api_key: API密钥
        user_desc: 用户描述

    Returns:
        分析结果
    """
    detector = ScamDetector(api_key=api_key)
    return detector.analyze_screenshot(image_path, user_desc)


if __name__ == "__main__":
    print("诈骗软件识别模块测试（硅基流动 API 版）")
    print("模型: Qwen/Qwen3.6-35B-A3B")
    print("请使用 scam_check_cli.py 或 scam_check_web.py 进行实际分析")