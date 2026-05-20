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

# 计算雷达图数据，处理 NaN 值
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
            norm_desc[FEATURE_LABELS[k]] = norm_value  # 返回数字类型
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
        "result_text": "AI Generated (Rule)" if prob_fake >= 0.5 else "Real Image",
        "radar_features": radar,
        "norm_features": norm_desc
    }
}

print("返回的数据:")
print(json.dumps(result, indent=2, ensure_ascii=False))
print("\n数据类型检查:")
print(f"prob_fake 类型: {type(result['data']['prob_fake'])}")
print(f"norm_features 类型: {type(result['data']['norm_features'])}")
for key, value in result['data']['norm_features'].items():
    print(f"  {key}: {type(value)} = {value}")