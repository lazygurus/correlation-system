import numpy as np
import pandas as pd
from sklearn.metrics import pairwise_distances
from scipy.stats import entropy

def zscore_standardize_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    按行做 Z-score 标准化
    """
    row_mean = df.mean(axis=1).values.reshape(-1, 1)  # 每行均值
    row_std = (df.std(axis=1) + 1e-12).values.reshape(-1, 1)  # 每行标准差
    return (df - row_mean) / row_std

def gaussian_discretization_fast(df: pd.DataFrame, sigma: float = 1.0, bins: int = 7,
                                 return_zscore: bool = True) -> pd.DataFrame:
    """
    高斯离散化（按行均值和标准差，自适应离散化），向量化加速版
    df: 原始 DataFrame
    sigma: 高斯核标准差
    bins: 离散等级数量（默认 7 => z-score 中 -3~3）
    return_zscore: True 返回离散等级，False 返回原值中心
    """
    data = df.to_numpy()

    # 每行均值与标准差
    mu = data.mean(axis=1, keepdims=True)
    std = data.std(axis=1, keepdims=True) + 1e-12
    print(mu.shape, std.shape)
    mu = mu.squeeze()  # (387,)
    std = std.squeeze()  # (387,)
    print(mu.shape, std.shape)
    # 在 z-score 空间生成中心点
    z_centers = np.linspace(-3, 3, bins)  # (bins,)
    centers = mu[None, :]  + std[None, :]  * z_centers[:, None]  # shape: (bins, n_samples)

    # 广播计算权重
    # data: (n_samples, n_features)
    # centers.T: (n_samples, bins) → 需要扩展成 (n_samples, bins, 1)
    diff = data[:, None, :] - centers.T[:, :, None]  # (n_samples, bins, n_features)
    weights = np.exp(-0.5 * (diff / sigma) ** 2)  # (n_samples, bins, n_features)

    # 找到最大权重对应的索引
    idx = np.argmax(weights, axis=1)  # (n_samples, n_features)

    if return_zscore:
        result = z_centers[idx]
    else:
        # 转换 idx → 对应原值中心
        result = np.take_along_axis(centers.T[:, :, None], idx[:, :, None], axis=1).squeeze(1)

    return pd.DataFrame(result, index=df.index, columns=df.columns)


def information_distance(df: pd.DataFrame) -> np.ndarray:
    """
    计算信息距离矩阵（基于对称 KL 散度）
    使用 softmax 保证输入为概率分布
    """
    data = df.to_numpy()
    shifted = data - np.max(data, axis=1, keepdims=True)
    exp_data = np.exp(shifted)
    prob_data = exp_data / (exp_data.sum(axis=1, keepdims=True) + 1e-12)

    n_samples = prob_data.shape[0]
    dist_matrix = np.zeros((n_samples, n_samples))

    for i in range(n_samples):
        for j in range(i + 1, n_samples):
            kl_ij = entropy(prob_data[i], prob_data[j])
            kl_ji = entropy(prob_data[j], prob_data[i])
            dist = 0.5 * (kl_ij + kl_ji)
            dist_matrix[i, j] = dist
            dist_matrix[j, i] = dist

    return dist_matrix


def compute_distance_matrix(df: pd.DataFrame, method: str = "euclidean", sigma: float = 1.0, bins: int = 7,
                            return_zscore: bool = True) -> np.ndarray:
    """
    计算距离矩阵
    method:
        - "euclidean": 用标准化数据计算欧式距离
        - "information": 用离散化数据计算信息距离
    """
    # 先检查第一列是否为字符串，如果是的话，就将其转换为行索引
    first_col = df.iloc[:, 0]
    if first_col.dtype == 'object' or isinstance(first_col.iloc[0], str):
        df = df.set_index(df.columns[0])  # 把第一列作为索引

    if method == "euclidean":
        standardized_df = zscore_standardize_rows(df)
        return pairwise_distances(standardized_df, metric="euclidean")
    elif method == "information":
        discretized_df = gaussian_discretization_fast(df, sigma=sigma, bins=bins, return_zscore=return_zscore)
        return information_distance(discretized_df)
    else:
        raise ValueError(f"未知的距离计算方法: {method}")

if __name__ == "__main__":
    df = pd.read_csv("D:\python\Relevance_System\data\statisticsData.txt" , encoding="gbk" , sep="\t" ,index_col=0)
    pd = gaussian_discretization_fast(df)
    print(pd)