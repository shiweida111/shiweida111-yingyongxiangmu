import os
import base64
from dotenv import load_dotenv
from openai import OpenAI

# 1. 配置和初始化
load_dotenv()
try:
    MY_API_KEY = "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"
    client = OpenAI(api_key=MY_API_KEY)  # ✅ 直接传递密钥
except Exception as e:
    print(f"初始化 OpenAI 客户端失败：{e}")
    exit()


# 2. 图像编码函数
def encode_image_to_base64(image_path):
    """
    将本地图片文件编码为 Base64 字符串。
    OpenAI API 要求本地图片以 Base64 格式传输。
    """
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"错误: 找不到文件 {image_path}")
        return None
    except Exception as e:
        print(f"编码文件时发生错误: {e}")
        return None


# 3. API 调用和推理函数
def analyze_scam_image(image_path, user_query):
    """
    调用 GPT-4o 或 GPT-4V 模型分析图像内容。
    """
    base64_image = encode_image_to_base64(image_path)
    if not base64_image:
        return "无法进行推理，因为图片文件处理失败。"

    # Base64 图像的数据 URI 格式
    image_uri = f"data:image/jpeg;base64,{base64_image}"

    try:
        response = client.chat.completions.create(
            # 推荐使用 gpt-4o (性能和速度都更优)
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的安全分析师，请根据用户的问题和提供的图片，判断图片内容是否可能涉及金融诈骗、网络钓鱼、虚假宣传等欺诈行为。请以中文清晰地说明你的判断依据和风险等级。"
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_query},
                        {
                            "type": "image_url",
                            "image_url": {"url": image_uri}  # 传递 Base64 图像
                        }
                    ],
                }
            ],
            max_tokens=500,
            temperature=0.1  # 调低温度以获取更严谨的判断
        )

        # 提取模型回复
        if response.choices:
            return response.choices[0].message.content
        else:
            return "模型未返回有效回复。"

    except Exception as e:
        return f"调用 API 时发生错误: {e}"


# 4. 主程序调用
if __name__ == "__main__":
    # 替换成你本地的图片路径
    local_image_path = r"./test_images/ChatGPT Image 2025年10月15日 15_17_50.png"

    # 你想向模型提问的问题
    prompt = "请分析这张截图，它声称能够提供高收益投资，是不是一个诈骗广告？请说明理由。"

    print(f"正在分析图片: {local_image_path}...")

    # ⚠️ 请确保替换上面的路径为你本地存在的图片文件路径

    analysis_result = analyze_scam_image(local_image_path, prompt)

    print("\n" + "=" * 30)
    print("🤖 诈骗风险分析结果:")
    print(analysis_result)
    print("=" * 30)