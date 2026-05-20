"""
诈骗软件检测报告生成模块
功能：生成专业的检测报告（支持 TXT 和 PDF 格式）
"""

import os
import json
from datetime import datetime
from pathlib import Path


class ReportGenerator:
    """检测报告生成器"""

    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_report_id(self):
        """生成唯一报告ID"""
        return datetime.now().strftime("%Y%m%d%H%M%S")

    def parse_analysis_result(self, analysis_text):
        """
        解析 AI 返回的分析结果，提取关键信息

        Args:
            analysis_text: AI 原始分析文本

        Returns:
            dict: 解析后的结构化数据
        """
        lines = analysis_text.split('\n')
        parsed = {
            "risk_level": "未知",
            "scam_type": "无法确定",
            "confidence": "未知",
            "key_findings": [],
            "warnings": [],
            "raw_text": analysis_text
        }

        analysis_lower = analysis_text.lower()

        if "极高风险" in analysis_text or "确定是诈骗" in analysis_text or "高风险" in analysis_text:
            parsed["risk_level"] = "高风险" if "极高风险" not in analysis_text else "极高风险"
            parsed["warnings"].append("检测到高风险特征，建议立即停止使用该软件")
        elif "中风险" in analysis_text:
            parsed["risk_level"] = "中风险"
            parsed["warnings"].append("检测到可疑特征，请谨慎使用")
        elif "低风险" in analysis_text:
            parsed["risk_level"] = "低风险"

        if "投资诈骗" in analysis_text:
            parsed["scam_type"] = "投资诈骗"
        elif "仿冒诈骗" in analysis_text or "仿冒" in analysis_text:
            parsed["scam_type"] = "仿冒诈骗"
        elif "钓鱼诈骗" in analysis_text or "钓鱼" in analysis_text:
            parsed["scam_type"] = "钓鱼诈骗"
        elif "色情诈骗" in analysis_text or "涉黄" in analysis_text:
            parsed["scam_type"] = "色情诈骗"
        elif "传销诈骗" in analysis_text or "传销" in analysis_text:
            parsed["scam_type"] = "传销诈骗"

        for keyword in ["高收益", "零风险", "日赚", "稳赚", "充值", "转账", "验证码", "密码"]:
            if keyword in analysis_text:
                parsed["key_findings"].append(f"检测到敏感关键词: {keyword}")

        import re
        confidence_match = re.search(r'(\d{1,3})%', analysis_text)
        if confidence_match:
            parsed["confidence"] = f"{confidence_match.group(1)}%"

        return parsed

    def generate_txt_report(self, image_path, analysis_result, user_description=None):
        """
        生成 TXT 格式的检测报告

        Args:
            image_path: 被检测的图片路径
            user_description: 用户描述

        Returns:
            str: 报告文件路径
        """
        report_id = self.generate_report_id()
        filename = f"scam_report_{report_id}.txt"
        filepath = os.path.join(self.output_dir, filename)

        parsed = self.parse_analysis_result(analysis_result["result"])

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("        诈骗软件检测报告\n")
            f.write("        Scam Software Detection Report\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"报告编号: {report_id}\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"被检测文件: {os.path.basename(image_path)}\n")
            if user_description:
                f.write(f"用户描述: {user_description}\n")
            f.write("\n" + "-" * 60 + "\n")

            f.write("\n【一、风险评估结果】\n\n")
            f.write(f"  风险等级: {parsed['risk_level']}\n")
            f.write(f"  诈骗类型: {parsed['scam_type']}\n")
            f.write(f"  置信度: {parsed['confidence']}\n")

            if parsed['warnings']:
                f.write("\n  [!] 风险警告:\n")
                for warning in parsed['warnings']:
                    f.write(f"    - {warning}\n")

            f.write("\n" + "-" * 60 + "\n")
            f.write("\n【二、关键发现】\n\n")
            if parsed['key_findings']:
                for finding in parsed['key_findings']:
                    f.write(f"  - {finding}\n")
            else:
                f.write("  未发现明显风险关键词\n")

            f.write("\n" + "-" * 60 + "\n")
            f.write("\n【三、详细分析】\n\n")
            f.write(analysis_result["result"])
            f.write("\n")

            f.write("\n" + "-" * 60 + "\n")
            f.write("\n【四、安全建议】\n\n")
            f.write("  1. 如果该软件被判定为高风险或极高风险，请立即停止使用\n")
            f.write("  2. 不要向任何未知或可疑的软件转账、充值\n")
            f.write("  3. 不要在任何可疑软件中输入银行账号、密码或验证码\n")
            f.write("  4. 如已受骗，请立即联系银行冻结账户并报警\n")
            f.write("  5. 下载软件请通过官方应用商店或官方网站\n")

            f.write("\n" + "-" * 60 + "\n")
            f.write("\n【五、免责声明】\n\n")
            f.write("  本报告由 AI 自动生成，仅供参考，不作为法律依据。\n")
            f.write("  检测结果可能因截图质量、AI 模型局限性等因素存在误差。\n")
            f.write("  如有疑问，请咨询专业人士或相关机构。\n")

            f.write("\n" + "=" * 60 + "\n")
            f.write(f"  报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n")

        return filepath

    def generate_json_report(self, image_path, analysis_result, user_description=None):
        """
        生成 JSON 格式的检测报告

        Args:
            image_path: 被检测的图片路径
            user_description: 用户描述

        Returns:
            str: 报告文件路径
        """
        report_id = self.generate_report_id()
        filename = f"scam_report_{report_id}.json"
        filepath = os.path.join(self.output_dir, filename)

        parsed = self.parse_analysis_result(analysis_result["result"])

        report_data = {
            "report_id": report_id,
            "generated_at": datetime.now().isoformat(),
            "image_file": os.path.basename(image_path),
            "user_description": user_description,
            "risk_assessment": {
                "risk_level": parsed["risk_level"],
                "scam_type": parsed["scam_type"],
                "confidence": parsed["confidence"]
            },
            "key_findings": parsed["key_findings"],
            "warnings": parsed["warnings"],
            "detailed_analysis": analysis_result["result"],
            "safety_recommendations": [
                "如果该软件被判定为高风险，请立即停止使用",
                "不要向任何未知或可疑的软件转账、充值",
                "不要在任何可疑软件中输入银行账号、密码或验证码",
                "如已受骗，请立即联系银行冻结账户并报警",
                "下载软件请通过官方应用商店或官方网站"
            ],
            "disclaimer": "本报告由 AI 自动生成，仅供参考，不作为法律依据"
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)

        return filepath

    def generate_markdown_report(self, image_path, analysis_result, user_description=None):
        """
        生成 Markdown 格式的检测报告

        Args:
            image_path: 被检测的图片路径
            user_description: 用户描述

        Returns:
            str: 报告文件路径
        """
        report_id = self.generate_report_id()
        filename = f"scam_report_{report_id}.md"
        filepath = os.path.join(self.output_dir, filename)

        parsed = self.parse_analysis_result(analysis_result["result"])

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# 🚨 诈骗软件检测报告\n\n")
            f.write(f"**报告编号**: {report_id}\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**被检测文件**: {os.path.basename(image_path)}\n\n")
            if user_description:
                f.write(f"**用户描述**: {user_description}\n\n")

            f.write("---\n\n")

            f.write("## 一、风险评估结果\n\n")
            f.write(f"| 项目 | 结果 |\n")
            f.write(f"|------|------|\n")
            f.write(f"| 风险等级 | **{parsed['risk_level']}** |\n")
            f.write(f"| 诈骗类型 | {parsed['scam_type']} |\n")
            f.write(f"| 置信度 | {parsed['confidence']} |\n\n")

            if parsed['warnings']:
                f.write("### ⚠️ 风险警告\n\n")
                for warning in parsed['warnings']:
                    f.write(f"- {warning}\n")
                f.write("\n")

            f.write("---\n\n")
            f.write("## 二、关键发现\n\n")
            if parsed['key_findings']:
                for finding in parsed['key_findings']:
                    f.write(f"- {finding}\n")
            else:
                f.write("未发现明显风险关键词\n")
            f.write("\n")

            f.write("---\n\n")
            f.write("## 三、详细分析\n\n")
            f.write(analysis_result["result"])
            f.write("\n\n")

            f.write("---\n\n")
            f.write("## 四、安全建议\n\n")
            f.write("1. 如果该软件被判定为高风险，请立即停止使用\n")
            f.write("2. 不要向任何未知或可疑的软件转账、充值\n")
            f.write("3. 不要在任何可疑软件中输入银行账号、密码或验证码\n")
            f.write("4. 如已受骗，请立即联系银行冻结账户并报警\n")
            f.write("5. 下载软件请通过官方应用商店或官方网站\n\n")

            f.write("---\n\n")
            f.write("## 五、免责声明\n\n")
            f.write("> 本报告由 AI 自动生成，仅供参考，不作为法律依据。\n")
            f.write("> 检测结果可能因截图质量、AI 模型局限性等因素存在误差。\n")
            f.write("> 如有疑问，请咨询专业人士或相关机构。\n\n")

            f.write("---\n\n")
            f.write(f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        return filepath


def generate_report(image_path, analysis_result, user_description=None, format='txt'):
    """
    便捷函数：生成检测报告

    Args:
        image_path: 被检测的图片路径
        analysis_result: 分析结果
        user_description: 用户描述
        format: 报告格式 ('txt', 'json', 'md')

    Returns:
        str: 报告文件路径
    """
    generator = ReportGenerator()

    if format == 'json':
        return generator.generate_json_report(image_path, analysis_result, user_description)
    elif format == 'md':
        return generator.generate_markdown_report(image_path, analysis_result, user_description)
    else:
        return generator.generate_txt_report(image_path, analysis_result, user_description)


if __name__ == "__main__":
    print("报告生成模块测试")
    print("请通过 scam_check_cli.py 或 scam_check_web.py 生成实际报告")
