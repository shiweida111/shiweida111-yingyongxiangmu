import base64
import traceback
from openai import OpenAI

# 配置
OPENAI_API_KEY = "sk-wcmsrwlipjimpyvitqlvzatveiuckzhigcanzxlzdlvymieg"
model = "Qwen/Qwen3.6-35B-A3B"

def test_llm():
    try:
        client = OpenAI(
            base_url='https://api.siliconflow.cn/v1',
            api_key=OPENAI_API_KEY
        )

        # 创建一个简单的测试消息
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "你好，测试一下"}
            ],
            max_tokens=100
        )
        
        result = response.choices[0].message.content
        print(f"[SUCCESS] 大模型调用成功!")
        print(f"响应内容: {result}")
        return True
        
    except Exception as e:
        print(f"[ERROR] 大模型调用失败: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_llm()