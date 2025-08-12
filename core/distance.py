import numpy as np
from sklearn.metrics import pairwise_distances
from scipy.stats import entropy


def gaussian_discretization(data: np.ndarray, sigma: float = 1.0) -> np.ndarray:
    """
    使用高斯公式对数据进行离散化
    data: 原始二维数据 (样本 × 特征)
    sigma: 高斯核的标准差
    """
    # 归一化数据到 [0, 1]
    data_min = data.min(axis=0)
    data_max = data.max(axis=0)
    norm_data = (data - data_min) / (data_max - data_min + 1e-12)

    # 高斯离散化：以均匀分布的中心点做模糊映射
    bins = 10  # 离散化等级
    centers = np.linspace(0, 1, bins)
    discretized = np.zeros_like(norm_data)

    for i in range(norm_data.shape[1]):
        for j in range(norm_data.shape[0]):
            # 计算该值到每个中心的高斯权重，选权重最大的中心
            weights = np.exp(-0.5 * ((norm_data[j, i] - centers) / sigma) ** 2)
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

# 最终是直接调用这个函数
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
