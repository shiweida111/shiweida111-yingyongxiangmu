# detect_image_xgb.py
"""
AI生成图像检测 — 单张图像实时检测模块
"""

import os
import joblib
import numpy as np
import cv2
import re
from datetime import datetime
from unit.lightweight_ai_detect import extract_features_from_path

# === 路径设置和常量 ===
MODEL_PATH = r"./ai_gen_detector_xgb.joblib"
LOG_PATH = r"./privacy_audit.log"
TEST_IMAGE_FOLDER = r"./test_images"  # 单张或多张测试图像的文件夹
THRESHOLD = 0.5


# -------------------------------
# 隐私检测函数 (复制自训练文件)
# -------------------------------
def detect_privacy_risk(image_path):
    """
    检测图像中可能的隐私风险：
    - 是否包含人脸
    - 文件名/路径启发
    """
    risk_score = 0.0
    details = []

    # 1. 检测人脸
    try:
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        img = cv2.imread(image_path)
        if img is None:
            return 0.0, ["图像无法读取"]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        if len(faces) > 0:
            risk_score += 0.4
            details.append(f"检测到 {len(faces)} 张人脸")
    except Exception as e:
        details.append(f"人脸检测失败: {e}")

    # 2. 文件名/路径启发
    if "id" in image_path.lower() or "private" in image_path.lower() or "ssn" in image_path.lower():
        risk_score += 0.1
        details.append("文件名/路径可能含隐私标识")

    return min(risk_score, 1.0), details


# -------------------------------
# 审计日志记录函数 (复制自训练文件)
# -------------------------------
def log_privacy_event(event_type, image_path, score, details, context=""):
    """将隐私事件写入审计日志。"""
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write("=" * 50 + "\n")
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {event_type.upper()}\n")
        f.write(f"  图像路径: {image_path}\n")
        if context:
            f.write(f"  模型上下文: {context}\n")
        f.write(f"  隐私风险评分: {score:.2f}\n")
        for d in details:
            f.write(f"    - {d}\n")
        f.write("=" * 50 + "\n\n")


# -------------------------------
# 主检测函数
# -------------------------------
def detect_single_image(image_path, model_data):
    """
    对单张图像进行 AI 生成检测和隐私风险评估。
    """
    scaler = model_data["scaler"]
    clf = model_data["clf"]

    # 1. 特征提取
    try:
        feats_dict = extract_features_from_path(image_path)
        feats_array = np.array([[
            feats_dict['hf_ratio'],
            feats_dict['lbp_entropy'],
            feats_dict['lbp_chisq'],
            feats_dict['residual_ratio'],
            feats_dict['lap_var'],
            feats_dict['s_var'],  # 新增
            feats_dict['v_var']  # 新增
        ]])
    except Exception as e:
        print(f"❌ 特征提取失败: {image_path}. 错误: {e}")
        return None, None

    # 2. 特征归一化
    X_scaled = scaler.transform(feats_array)

    # 3. 模型预测
    prob_fake = clf.predict_proba(X_scaled)[:, 1][0]
    pred_class = 1 if prob_fake >= THRESHOLD else 0
    result_text = "AI生成图像" if pred_class == 1 else "真实图像"

    # 4. 隐私风险检测
    risk_score, risk_details = detect_privacy_risk(image_path)

    print("-" * 40)
    print(f"🖼️ 检测文件: {os.path.basename(image_path)}")
    print(f"  AI 伪造概率: {prob_fake:.4f}")
    print(f"  模型判定结果: {result_text}")
    print(f"  隐私风险评分: {risk_score:.2f}")

    if risk_score > 0:
        print("  🚨 风险详情:")
        for detail in risk_details:
            print(f"    - {detail}")

        # 记录到日志 (高风险或高概率AI伪造)
        if risk_score >= 0.3 or prob_fake >= 0.8:
            context = f"模型概率={prob_fake:.4f}, 判定={result_text}"
            log_privacy_event("SINGLE_IMAGE_HIGH_RISK", image_path, risk_score, risk_details, context)
            print(f"  ⚠️ 已将风险事件记录到 {LOG_PATH}")

    return prob_fake, pred_class


# -------------------------------
# 程序主入口
# -------------------------------
if __name__ == "__main__":
    if not os.path.exists(TEST_IMAGE_FOLDER):
        print(f"❌ 错误: 测试图像文件夹 '{TEST_IMAGE_FOLDER}' 不存在。请创建该文件夹并放入图像。")
        exit()

    # 1. 加载模型和 Scaler
    if not os.path.exists(MODEL_PATH):
        print(f"❌ 错误: 模型文件 '{MODEL_PATH}' 不存在。请先运行 train_and_eval_xgb.py 进行训练。")
        exit()

    try:
        model_data = joblib.load(MODEL_PATH)
        print(f"✅ 模型和归一化器已从 {MODEL_PATH} 加载。")
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        exit()

    # 2. 遍历测试文件夹中的所有图像
    print(f"\n🚀 开始检测文件夹 '{TEST_IMAGE_FOLDER}' 中的图像...")

    image_files = [
        os.path.join(TEST_IMAGE_FOLDER, f)
        for f in os.listdir(TEST_IMAGE_FOLDER)
        if f.lower().endswith(('.jpg', '.png', '.jpeg'))
    ]

    if not image_files:
        print(f"⚠️ 警告: 文件夹 '{TEST_IMAGE_FOLDER}' 中未找到任何图像文件。")

    for image_path in image_files:
        detect_single_image(image_path, model_data)

    print("\n✅ 所有图像检测完成。")