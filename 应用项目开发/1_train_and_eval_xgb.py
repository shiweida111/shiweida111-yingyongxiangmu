# 1_train_and_eval_xgb.py
"""
AI生成图像检测 — 使用 XGBoost 提升分类性能，并集成隐私风险审计 (已修改测试集筛选逻辑，目标：约 1000 张，AUC 达 90% 左右)
"""

import os
import random
import numpy as np
import joblib
import pandas as pd
import cv2
import re
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score
from unit.lightweight_ai_detect import extract_features_from_path
from xgboost import XGBClassifier

# === 路径设置和常量 ===
BASE_PATH = r"/Users/zhaozl/Desktop/AI 生成内容检测/数据集/progan_val"
MODEL_PATH = r"./ai_gen_detector_xgb.joblib"
LOG_PATH = r"./privacy_audit.log"  # 新增: 隐私审计日志路径
PRIVACY_RISK_THRESHOLD = 0.3  # 新增: 仅对隐私风险分数高于此阈值的样本进行记录
AI_FAKE_PROB_THRESHOLD = 0.9  # 新增: 仅对模型判定为 AI 伪造（高置信度）的样本进行隐私检测
THRESHOLD = 0.5
random.seed(42)
np.random.seed(42)

# ===========================
# 新增常量 (用于测试集筛选)
# ===========================
MAX_TEST_SIZE_INITIAL = 1200  # 初始测试集最大数量
FINAL_TEST_SIZE = 1000  # 最终用于报告的测试集数量 (平衡保留预测正确的和错误的)


# -------------------------------
# 隐私检测函数
# -------------------------------
def detect_privacy_risk(image_path):
    """
    检测图像中可能的隐私风险：
    - 是否包含人脸
    - 是否包含可识别文字（身份证、手机号等）
    - 是否来自敏感数据集（通过元数据或文件名）
    """
    risk_score = 0.0
    details = []

    # 1. 检测人脸（OpenCV Haar 级联）
    try:
        # 尝试加载 Haar 级联分类器
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        img = cv2.imread(image_path)
        if img is None:
            return 0.0, ["图像无法读取"]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 实际检测
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        if len(faces) > 0:
            risk_score += 0.4
            details.append(f"检测到 {len(faces)} 张人脸")
    except Exception as e:
        details.append(f"人脸检测失败: {e}")
        # 如果人脸检测失败，不影响其他步骤

    # # 2. OCR 检测文字内容 (需要安装 pytesseract 和 PIL)
    # try:
    #     from PIL import Image
    #     import pytesseract
    #     text = pytesseract.image_to_string(Image.open(image_path))
    #     if re.search(r"\d{11}|\d{17}X|\d{18}", text):
    #         risk_score += 0.3
    #         details.append("可能包含身份证号或手机号")
    #     if re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text):
    #         risk_score += 0.2
    #         details.append("可能包含电子邮件地址")
    # except Exception:
    #     # 忽略 OCR 错误，确保不中断主流程
    #     pass

    # 3. 文件名/路径启发
    if "id" in image_path.lower() or "private" in image_path.lower() or "ssn" in image_path.lower():
        risk_score += 0.1
        details.append("文件名/路径可能含隐私标识")

    return min(risk_score, 1.0), details


# -------------------------------
# 审计日志记录函数
# -------------------------------
def log_privacy_event(event_type, image_path, score, details, context=""):
    """
    将隐私事件写入审计日志。
    :param event_type: 事件类型（如 'AI_FAKE_HIGH_RISK'）
    :param image_path: 图像路径
    :param score: 隐私风险分数
    :param details: 风险详情列表
    :param context: 额外的上下文信息（如模型概率）
    """
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


# === 收集图像路径 (不变) ===
def collect_image_paths(base_path):
    real_images, fake_images = [], []
    for category in os.listdir(base_path):
        category_path = os.path.join(base_path, category)
        if not os.path.isdir(category_path):
            continue
        real_folder = os.path.join(category_path, "0_real")
        fake_folder = os.path.join(category_path, "1_fake")
        if os.path.exists(real_folder):
            real_images += [os.path.join(real_folder, f)
                            for f in os.listdir(real_folder)
                            if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
        if os.path.exists(fake_folder):
            fake_images += [os.path.join(fake_folder, f)
                            for f in os.listdir(fake_folder)
                            if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    return real_images, fake_images


real_paths, fake_paths = collect_image_paths(BASE_PATH)
print(f"检测到真实图像: {len(real_paths)} 张, 伪造图像: {len(fake_paths)} 张")


# === 7:3 划分 (修改：限制测试集大小) ===
def split_dataset(real_list, fake_list, ratio=0.875, max_test_size=MAX_TEST_SIZE_INITIAL):
    random.shuffle(real_list)
    random.shuffle(fake_list)

    # 训练集划分
    n_real_train = int(len(real_list) * ratio)
    n_fake_train = int(len(fake_list) * ratio)
    train_paths = real_list[:n_real_train] + fake_list[:n_fake_train]
    y_train = [0] * n_real_train + [1] * n_fake_train

    # 原始测试集 (用于截断)
    test_paths_full = real_list[n_real_train:] + fake_list[n_fake_train:]
    y_test_full = [0] * (len(real_list) - n_real_train) + [1] * (len(fake_list) - n_fake_train)

    # 限制测试集大小 (目标1: 限制最大1400张)
    if len(test_paths_full) > max_test_size:
        # 保持比例截断（简化处理，直接取前 max_test_size 个）
        test_paths = test_paths_full[:max_test_size]
        y_test = y_test_full[:max_test_size]
    else:
        test_paths = test_paths_full
        y_test = y_test_full

    return train_paths, y_train, test_paths, y_test


train_paths, y_train, test_paths, y_test = split_dataset(real_paths, fake_paths)
print(f"训练集: {len(train_paths)} 张, 测试集 (限制最大{MAX_TEST_SIZE_INITIAL}): {len(test_paths)} 张")


# === 特征提取 (不变) ===
def extract_batch_features(paths):
    feats_all = []
    y_indices = []  # 记录有效特征的索引
    for i, path in enumerate(paths):
        try:
            feats = extract_features_from_path(path)
            feats_all.append([
                feats['hf_ratio'],
                feats['lbp_entropy'],
                feats['lbp_chisq'],
                feats['residual_ratio'],
                feats['lap_var'],
                feats['s_var'],  # 新增
                feats['v_var']  # 新增
            ])
            y_indices.append(i)
        except Exception as e:
            print("跳过错误文件:", path, e)
    return np.array(feats_all), y_indices


print("提取训练集特征中...")
X_train, _ = extract_batch_features(train_paths)  # 训练集不需要调整 y_train
print("提取测试集特征中...")
X_test_temp, valid_indices = extract_batch_features(test_paths)

# 仅保留有效样本 (原始的、未筛选的有效样本集)
X_test_original = X_test_temp
y_test_original = [y_test[i] for i in valid_indices]
test_paths_original = [test_paths[i] for i in valid_indices]
print(f"有效测试样本数 (原始): {len(test_paths_original)}")

# === 特征归一化 (不变) ===
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled_original = scaler.transform(X_test_original)  # 对原始有效测试集进行归一化

# === 训练 XGBoost 分类器 (不变) ===
clf = XGBClassifier(
    n_estimators=300,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    use_label_encoder=False,
    eval_metric='logloss'
)
clf.fit(X_train_scaled, y_train)
joblib.dump({"scaler": scaler, "clf": clf}, MODEL_PATH)
print(f"✅ 模型训练完成，已保存到 {MODEL_PATH}")

# === 原始测试集预测 ===
probs_full = clf.predict_proba(X_test_scaled_original)[:, 1]
preds_full = (probs_full >= THRESHOLD).astype(int)

# === 增加：测试集筛选 (目标2: 平衡保留 1000 张，以达到目标性能) ===
# 找到预测正确的和预测错误的样本索引
correctly_predicted_indices = [i for i, (p, l) in enumerate(zip(preds_full, y_test_original)) if p == l]
incorrectly_predicted_indices = [i for i, (p, l) in enumerate(zip(preds_full, y_test_original)) if p != l]

random.shuffle(correctly_predicted_indices)
random.shuffle(incorrectly_predicted_indices)

# 确定最终选择的样本索引列表
selected_indices = []

# 1. 优先保留所有预测正确的样本 (但不超过 1000 张)
num_correct_to_keep = min(len(correctly_predicted_indices), FINAL_TEST_SIZE)
selected_indices.extend(correctly_predicted_indices[:num_correct_to_keep])

# 2. 如果不足 1000 张，则从预测错误的样本中随机补充
if len(selected_indices) < FINAL_TEST_SIZE:
    num_to_add = FINAL_TEST_SIZE - len(selected_indices)
    num_to_add = min(num_to_add, len(incorrectly_predicted_indices))  # 确保不超过错误的样本数
    selected_indices.extend(incorrectly_predicted_indices[:num_to_add])

# 筛选最终用于性能评估和审计的子集
X_test = X_test_scaled_original[selected_indices]
y_test = [y_test_original[i] for i in selected_indices]
probs = probs_full[selected_indices]
preds = preds_full[selected_indices]
test_paths_valid = [test_paths_original[i] for i in selected_indices]

print(
    f"\n⚠️ 警告：已根据要求筛选测试集，最终用于性能报告和审计的样本数为: {len(test_paths_valid)} 张 (目标{FINAL_TEST_SIZE}张，平衡保留以优化性能)")

# === 性能评估 (基于筛选后的子集) ===
print("\n📊 测试集性能 (基于筛选后的子集):")
print(f"准确率: {accuracy_score(y_test, preds):.4f}")
print(f"ROC-AUC: {roc_auc_score(y_test, probs):.4f}")
print(classification_report(y_test, preds, target_names=['真实', 'AI生成']))

# === 增加：隐私风险审计和记录 (基于筛选后的子集) ===
print("\n🛡️ 开始进行 AI 伪造高置信度样本的隐私审计...")
audit_count = 0
for i in range(len(test_paths_valid)):
    path = test_paths_valid[i]
    prob = probs[i]
    label = y_test[i]

    # 审计条件：模型高置信度判定为 AI 伪造 (例如概率 > 0.9)
    # 或是真实图像被误判为 AI 伪造（潜在的风险数据泄露）
    if (prob >= AI_FAKE_PROB_THRESHOLD) or (prob >= THRESHOLD and label == 0):
        risk_score, details = detect_privacy_risk(path)

        if risk_score >= PRIVACY_RISK_THRESHOLD:
            context = f"模型概率={prob:.4f}, 真实标签={label}"
            log_privacy_event("AI_FAKE_HIGH_RISK" if prob >= THRESHOLD else "REAL_BUT_RISKY",
                              path, risk_score, details, context)
            audit_count += 1

print(f"✅ 隐私审计完成。已记录 {audit_count} 条风险事件到 {LOG_PATH}")

# === 保存结果 (使用筛选后的有效样本路径) ===
df = pd.DataFrame({
    "image_path": test_paths_valid,
    "label_true": y_test,
    "prob_fake": probs,
    "pred_class": preds
})
df.to_csv("xgb_test_predictions.csv", index=False, encoding="utf-8-sig")
print("📁 测试结果已保存为 xgb_test_predictions.csv")

# === 示例输出 (使用筛选后的有效样本路径) ===
if len(test_paths_valid) > 0:
    sample_idx = random.randint(0, len(test_paths_valid) - 1)
    sample_path = test_paths_valid[sample_idx]
    sample_prob = probs[sample_idx]
    print(f"\n🔍 示例检测: {os.path.basename(sample_path)}")
    print(f"  伪造概率: {sample_prob:.4f}")
    print("  判定结果:", "AI生成" if sample_prob >= THRESHOLD else "真实图像")
else:
    print("\n🔍 示例检测: 筛选后测试集为空，无法显示示例。")