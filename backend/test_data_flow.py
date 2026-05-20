import json
import numpy as np
from unit.lightweight_ai_detect import extract_features_from_path, heuristic_score

# 定义中文标签
FEATURE_LABELS = {
    "hf_ratio": "高频能量比",
    "lbp_entropy": "纹理熵",
    "lbp_chisq": "局部二值模式",
    "residual_ratio": "噪声残差比",
    "lap_var": "拉普拉斯方差",
    "s_var": "饱和度方差",
    "v_var": "亮度方差"
}

NORM_MAX_VALUES = {
    "hf_ratio": 0.5,
    "lbp_entropy": 8.0,
    "lbp_chisq": 1000.0,
    "residual_ratio": 0.1,
    "lap_var": 800.0,
    "s_var": 0.1,
    "v_var": 0.1
}

# 模拟后端处理
features = extract_features_from_path('test.jpg')

# 处理 NaN 值
for k, v in features.items():
    if isinstance(v, float) and np.isnan(v):
        features[k] = 0.0

prob_fake, _ = heuristic_score(features)
result_text = "AI Generated (Rule)" if prob_fake >= 0.5 else "Real Image"

# 回退到传统特征分析（模拟大模型失败）
radar = {}
norm_desc = {}
for k, v in features.items():
    if k in FEATURE_LABELS:
        try:
            v = float(v)
            if np.isnan(v) or np.isinf(v):
                v = 0.0
            norm_value = min(v / NORM_MAX_VALUES[k], 1.0)
            if np.isnan(norm_value) or np.isinf(norm_value):
                norm_value = 0.0
            radar[FEATURE_LABELS[k]] = round(norm_value, 4)
            norm_desc[FEATURE_LABELS[k]] = norm_value
        except:
            radar[FEATURE_LABELS[k]] = 0.0
            norm_desc[FEATURE_LABELS[k]] = 0.0

# 构建返回数据
result = {
    "success": True,
    "code": 200,
    "message": "Detection completed",
    "data": {
        "prob_fake": prob_fake,
        "result_text": result_text,
        "radar_features": radar,
        "norm_features": norm_desc,
        "risk_score": "0.00",
        "risk_details": [],
        "image_url": "http://localhost:5173/uploads/test.jpg",
        "detect_time": "2024-01-01 12:00:00"
    }
}

# 模拟前端处理
print("=== 后端返回数据 ===")
print(json.dumps(result, indent=2, ensure_ascii=False))

print("\n=== 前端处理测试 ===")
data = result['data']

# 处理 prob_fake
if hasattr(data['prob_fake'], 'item'):
    data['prob_fake'] = data['prob_fake'].item()
print(f"prob_fake: {data['prob_fake']} (类型: {type(data['prob_fake']).__name__})")

# 转换 norm_features 为数组
featureArray = []
for key in data['norm_features']:
    value = float(data['norm_features'][key])
    featureArray.append({
        'name': key,
        'value': value
    })
print(f"\n转换后的特征数组:")
for item in featureArray:
    print(f"  {item['name']}: {item['value']}")

print("\n=== JSON序列化测试 ===")
json_str = json.dumps(result)
print(f"JSON字符串长度: {len(json_str)}")

# 解析测试
parsed = json.loads(json_str)
print(f"\n解析后的 prob_fake: {parsed['data']['prob_fake']} (类型: {type(parsed['data']['prob_fake']).__name__})")
print(f"解析后的 norm_features: {parsed['data']['norm_features']}")