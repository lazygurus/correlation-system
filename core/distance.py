import numpy as np
from sklearn.metrics import pairwise_distances
from scipy.stats import entropy

def gaussian_discretization(data: np.ndarray, sigma: float = 1.0, bins: int = 7) -> np.ndarray:
    """
    基于标准差的高斯离散化
    data: 原始二维数据 (样本 × 特征)
    sigma: 高斯核的标准差
    bins: 离散等级数量（默认 7 → 对应 -3 ~ 3）
    """
    discretized = np.zeros_like(data, dtype=float)

    for i in range(data.shape[1]):  # 按列（特征）处理
        mu = data[:, i].mean()
        std = data[:, i].std() + 1e-12  # 防止除0

        # 在 z-score 空间生成中心点（-3 ~ 3 均分）
        z_centers = np.linspace(-3, 3, bins)
        centers = mu + z_centers * std  # 转回原值空间

        # 遍历样本，匹配高斯权重最大值的中心
        for j in range(data.shape[0]):
            weights = np.exp(-0.5 * ((data[j, i] - centers) / sigma) ** 2)
            discretized[j, i] = centers[np.argmax(weights)]

    return discretized

def information_distance(data: np.ndarray) -> np.ndarray:
    """
    计算信息距离矩阵 (基于KL散度的对称度量)
    """
    n_samples = data.shape[0]
    dist_matrix = np.zeros((n_samples, n_samples))

    # 转为概率分布
    prob_data = data / (data.sum(axis=1, keepdims=True) + 1e-12)

    for i in range(n_samples):
        for j in range(i + 1, n_samples):
            kl_ij = entropy(prob_data[i], prob_data[j])
            kl_ji = entropy(prob_data[j], prob_data[i])
            dist = 0.5 * (kl_ij + kl_ji)  # 对称化
            dist_matrix[i, j] = dist
            dist_matrix[j, i] = dist

    return dist_matrix

def compute_distance_matrix(data: np.ndarray, method: str = "euclidean", sigma: float = 1.0) -> np.ndarray:
    """
    计算距离矩阵
    method: "euclidean" 或 "information"
    sigma: 高斯离散化标准差
    """
    # 高斯离散化
    discretized_data = gaussian_discretization(data, sigma=sigma)

    if method == "euclidean":
        return pairwise_distances(discretized_data, metric="euclidean")
    elif method == "information":
        return information_distance(discretized_data)
    else:
        raise ValueError(f"未知的距离计算方法: {method}")
