"""
lightweight_ai_detect.py

轻量级 AI 生成图像鉴伪（启发式 + 可选训练校准）
功能：
 - 计算频域高频能量比 (FFT)
 - 计算 LBP 直方图熵与距离特征
 - 计算噪声残差能量（中值滤波 residual）
 - 计算图像锐度（Laplacian variance）
 - **新增：计算色度分量方差 (Chroma variance)**
 - 将这些特征线性组合并通过 sigmoid 映射为伪造概率（0~1）
 - 可选：如果提供标注数据集，可以训练 logistic regression 校准权重
"""

import os
import math
import numpy as np
import cv2
from skimage.feature import local_binary_pattern
from skimage import color
from scipy import fftpack
from scipy.ndimage import median_filter
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import joblib


# ---------- 特征计算 ----------

def read_image(path):
    img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"不能读取图像: {path}")
    return img


def to_gray_float(img):
    # 返回 0..1 float 灰度图
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img.astype(np.float32) / 255.0


def fft_highfreq_ratio(gray, radius_ratio=0.25):
    """
    计算频域中高频能量占比。
    radius_ratio: 低频半径占比（越大认为低频越多），我们取 complement 作为高频。
    返回值: high_freq_energy / total_energy (0..1)
    """
    h, w = gray.shape
    # pad to next power of 2 speed (可选)
    F = fftpack.fftshift(fftpack.fft2(gray))
    mag = np.abs(F)
    cy, cx = h // 2, w // 2
    Y, X = np.ogrid[:h, :w]
    dist = np.sqrt((Y - cy) ** 2 + (X - cx) ** 2)
    maxr = np.sqrt(cx * cx + cy * cy)
    low_r = radius_ratio * maxr
    low_mask = dist <= low_r
    low_energy = (mag[low_mask] ** 2).sum()
    total_energy = (mag ** 2).sum() + 1e-12
    high_ratio = 1.0 - (low_energy / total_energy)
    return float(high_ratio)


def lbp_features(gray, P=8, R=1, n_bins=256):
    """
    计算 LBP 直方图及其熵 / 与均匀分布的距离等特征
    返回：
      hist_norm (n_bins) 以及 熵 和 chisq_dist
    """
    # skimage 的 LBP 接受 0..1 或 0..255 值 - 我传 0..1*255
    img_u8 = np.clip((gray * 255.0).astype(np.uint8), 0, 255)
    lbp = local_binary_pattern(img_u8, P, R, method="uniform")
    # 直方图
    max_bins = int(lbp.max()) + 1
    hist, _ = np.histogram(lbp.ravel(), bins=range(0, max_bins + 1), density=False)
    hist = hist.astype(float)
    hist_sum = hist.sum() + 1e-12
    hist_norm = hist / hist_sum
    # 熵
    entropy = -np.sum([p * math.log(p + 1e-12) for p in hist_norm])
    # 与均匀分布的 chisq 距离（度量异构性）
    uniform = np.ones_like(hist_norm) / len(hist_norm)
    chisq = 0.5 * np.sum(((hist_norm - uniform) ** 2) / (hist_norm + uniform + 1e-12))
    return {
        "lbp_entropy": float(entropy),
        "lbp_chisq": float(chisq),
        "lbp_hist": hist_norm
    }


def residual_noise_energy(gray, filter_size=3):
    """
    中值滤波残差能量：res = img - median_filter(img)
    返回 res 能量比（res_variance / img_variance）
    真实照片噪声通常与细节/传感器噪声相关，AI 图像可能在残差统计上不同。
    """
    med = median_filter(gray, size=filter_size)
    res = gray - med
    res_var = np.var(res)
    img_var = np.var(gray) + 1e-12
    return float(res_var / img_var)


def laplacian_variance(gray):
    lap = cv2.Laplacian((gray * 255).astype(np.uint8), cv2.CV_64F)
    return float(lap.var())


# --- 新增特征: 色度分量方差 ---
def chroma_variance(img):
    """
    计算 HSV 空间中色度分量 S 和 V 的方差（或只用 S 或 V）。
    AI 生成图像的色度统计可能与真实图像存在差异。
    """
    # 转换为 HSV 空间
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # 归一化到 0-1
    hsv_float = hsv.astype(np.float32)

    # 提取 S（Saturation, 饱和度）和 V（Value, 亮度）分量
    S = hsv_float[:, :, 1] / 255.0
    V = hsv_float[:, :, 2] / 255.0

    # 计算方差
    s_var = np.var(S)
    v_var = np.var(V)

    return {
        "s_var": float(s_var),
        "v_var": float(v_var)
    }


# ------------------------------

# ---------- 特征归一化与评分 ----------

def extract_features_from_path(path):
    img = read_image(path)
    gray = to_gray_float(img)
    features = {}
    features['hf_ratio'] = fft_highfreq_ratio(gray, radius_ratio=0.25)  # 越高可能越像 AI（启发式）
    lbp = lbp_features(gray, P=8, R=1)
    features.update({k: lbp[k] for k in ['lbp_entropy', 'lbp_chisq']})
    features['residual_ratio'] = residual_noise_energy(gray, filter_size=3)
    features['lap_var'] = laplacian_variance(gray)

    # 新增特征
    chroma = chroma_variance(img)
    features['s_var'] = chroma['s_var']
    features['v_var'] = chroma['v_var']

    return features


def heuristic_score(features, weights=None, feature_ranges=None):
    """
    将特征变换到 0..1 区间并做线性组合，然后通过 sigmoid 得到概率。
    weights: dict 指定各特征的权重（若 None 使用默认经验权重）
    feature_ranges: dict 指定每个特征的 (min,max) 用于归一化；若 None 使用经验范围
    """
    # 默认权重（经验值，可用训练来校准）- 新增特征默认权重
    default_weights = {
        'hf_ratio': 1.0,  # 高频比越高，倾向 AI（经验）
        'lbp_entropy': 0.6,  # LBP 熵越低/高具体如何取决数据，这里用正权重
        'lbp_chisq': 0.8,  # 与均匀分布差异，大差异有可能指纹不同
        'residual_ratio': 1.2,  # 残差占比，AI 图像残差统计可能不同
        'lap_var': -0.8,  # 锐度：通常 AI 图像某些生成器会偏锐/过度平滑，负权表示高锐度可能更像真实（经验）
        's_var': 0.5,  # S 方差，AI 伪影可能使色度方差不同
        'v_var': 0.3  # V 方差
    }
    if weights is None:
        weights = default_weights

    # 经验归一化区间（这些为建议范围；如果你要更可靠的概率，建议用训练数据拟合） - 新增特征经验范围
    default_ranges = {
        'hf_ratio': (0.0, 1.0),
        'lbp_entropy': (0.0, 6.0),  # 熵可能范围
        'lbp_chisq': (0.0, 2.0),
        'residual_ratio': (0.0, 1.0),
        'lap_var': (0.0, 5000.0),
        's_var': (0.0, 0.1),  # S 方差通常较小
        'v_var': (0.0, 0.2)  # V 方差
    }
    if feature_ranges is None:
        feature_ranges = default_ranges

    # 归一化并线性组合
    s = 0.0
    for k, w in weights.items():
        v = features.get(k, 0.0)
        vmin, vmax = feature_ranges.get(k, (0.0, 1.0))
        # clamp then normalize to 0..1
        if vmax - vmin <= 1e-6:
            vn = 0.0
        else:
            vn = (v - vmin) / (vmax - vmin)
            vn = max(0.0, min(1.0, vn))
        s += w * vn

    # Sigmoid mapping到概率
    prob = 1.0 / (1.0 + math.exp(-s + 0.0))  # bias 0.0，可以调整
    return prob, s


# ---------- 可选：用标注数据训练校准（logistic regression） ----------

def train_calibrator_from_folder(pos_folder, neg_folder, save_path=None):
    """
    pos_folder: 真实 AI 生成（label=1）或伪造的文件夹
    neg_folder: 真实照片（label=0）或相反，用户自己定义标签
    要求文件夹内是图像文件。
    返回训练好的 sklearn pipeline (StandardScaler + LogisticRegression)
    """
    X = []
    y = []
    for p in [(pos_folder, 1), (neg_folder, 0)]:
        folder, label = p
        for fname in os.listdir(folder):
            fp = os.path.join(folder, fname)
            try:
                feats = extract_features_from_path(fp)
                # 修改：增加新的特征
                vec = [feats['hf_ratio'], feats['lbp_entropy'], feats['lbp_chisq'],
                       feats['residual_ratio'], feats['lap_var'],
                       feats['s_var'], feats['v_var']]
                X.append(vec)
                y.append(label)
            except Exception as e:
                print("跳过文件", fp, "错误:", e)
    X = np.array(X)
    y = np.array(y)
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    clf = LogisticRegression(max_iter=200)
    clf.fit(Xs, y)
    pipeline = {"scaler": scaler, "clf": clf}
    if save_path:
        joblib.dump(pipeline, save_path)
    return pipeline


def predict_with_pipeline(path, pipeline):
    feats = extract_features_from_path(path)
    # 修改：增加新的特征
    vec = np.array([[feats['hf_ratio'], feats['lbp_entropy'], feats['lbp_chisq'],
                     feats['residual_ratio'], feats['lap_var'],
                     feats['s_var'], feats['v_var']]])
    Xs = pipeline['scaler'].transform(vec)
    prob = pipeline['clf'].predict_proba(Xs)[0, 1]
    return prob, feats


# ---------- CLI/示例用法 ----------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Lightweight AI-generated image detector (heuristic or trained)")
    parser.add_argument("image", help="待检测图像路径")
    parser.add_argument("--use-trained", default=None, help="已训练的 pipeline 文件（joblib），若提供则使用该模型输出概率")
    parser.add_argument("--show-features", action="store_true", help="打印中间特征")
    args = parser.parse_args()

    if args.use_trained:
        pipeline = joblib.load(args.use_trained)
        prob, feats = predict_with_pipeline(args.image, pipeline)
        print(f"使用训练校准模型 伪造概率: {prob:.4f}")
        if args.show_features:
            print("特征：", feats)
    else:
        feats = extract_features_from_path(args.image)
        prob, score = heuristic_score(feats)
        print(f"启发式 伪造概率: {prob:.4f}  (raw_score={score:.4f})")
        if args.show_features:
            print("特征：")
            for k, v in feats.items():
                print(f"  {k:20s}: {v}")