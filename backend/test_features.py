import cv2
import numpy as np

# 创建一个测试图像
test_img = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
cv2.imwrite('test.jpg', test_img)
print("Created test image")

# 测试特征提取
from unit.lightweight_ai_detect import extract_features_from_path

try:
    features = extract_features_from_path('test.jpg')
    print("Features extracted successfully:")
    for k, v in features.items():
        print(f"  {k}: {v}")
except Exception as e:
    print(f"Error extracting features: {e}")
    import traceback
    traceback.print_exc()