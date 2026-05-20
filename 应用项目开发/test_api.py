import json
import requests

# 测试后端API
url = 'http://localhost:5173/api/detect'
files = {'file': open('test.jpg', 'rb')}
data = {'model_type': 'heuristic'}

try:
    response = requests.post(url, files=files, data=data)
    result = response.json()
    
    print("=== API响应 ===")
    print(f"状态码: {response.status_code}")
    print(f"是否成功: {result.get('success')}")
    
    if result.get('success'):
        data = result['data']
        print(f"\n检测结果: {data.get('result_text')}")
        print(f"伪造概率: {data.get('prob_fake')}")
        print(f"prob_fake 类型: {type(data.get('prob_fake')).__name__}")
        
        print("\n特征分析:")
        norm_features = data.get('norm_features', {})
        for key, value in norm_features.items():
            print(f"  {key}: {value} (类型: {type(value).__name__})")
        
        # 测试前端处理逻辑
        print("\n=== 前端处理测试 ===")
        
        # 模拟前端处理 norm_features
        featureArray = []
        for key in norm_features:
            value = float(norm_features[key])
            normalizedValue = 0 if (isinstance(value, float) and (isnan(value) or not isfinite(value))) else value
            featureArray.append({
                'name': key,
                'value': normalizedValue
            })
        
        print("转换后的特征数组:")
        for item in featureArray:
            print(f"  {item['name']}: {item['value']}%")
            
except Exception as e:
    print(f"请求失败: {e}")