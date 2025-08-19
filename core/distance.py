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

def gaussian_discretization_fast(df: pd.DataFrame, sigma: float = 1.0, bins: int = 13,
                                 return_zscore: bool = True) -> pd.DataFrame:
    """
    高斯离散化（按行均值和标准差，自适应离散化），向量化加速版
    对于全相同值的行（标准差为 0），返回该值（return_zscore=False）或 z-score 0（return_zscore=True）

    df: 原始 DataFrame
    sigma: 高斯核标准差
    bins: 离散等级数量（默认 7 => z-score 中 -3~3）
    return_zscore: True 返回离散等级，False 返回原值中心
    """
    data = df.to_numpy()

    # 每行均值与标准差
    mu = data.mean(axis=1)
    std = data.std(axis=1)

    # 检测标准差为 0 的行（全相同值）
    zero_std_mask = std < 1e-12
    std_safe = std.copy()
    std_safe[zero_std_mask] = 1.0  # 临时设置 std=1 避免除 0

    # 在 z-score 空间生成中心点
    z_centers = np.linspace(-3, 3, bins)  # (bins,)
    centers = mu[None, :] + std_safe[None, :] * z_centers[:, None]  # shape: (bins, n_samples)

    # 广播计算权重
    diff = data[:, None, :] - centers.T[:, :, None]  # (n_samples, bins, n_features)
    weights = np.exp(-0.5 * (diff / sigma) ** 2)  # (n_samples, bins, n_features)

    # 找到最大权重对应的索引
    idx = np.argmax(weights, axis=1)  # (n_samples, n_features)

    if return_zscore:
        result = z_centers[idx]
        # 对全相同值的行返回 0
        result[zero_std_mask, :] = 0
    else:
        # 转换 idx → 对应原值中心
        result = np.take_along_axis(centers.T, idx, axis=1)
        # 对全相同值的行返回原值（均值）
        result[zero_std_mask, :] = mu[zero_std_mask, None]

    return pd.DataFrame(result, index=df.index, columns=df.columns)


def information_distance(discrete_df: pd.DataFrame, base: float = 2.0, ignore_na: bool=True) -> pd.DataFrame:
    rows = []
    for _, row in discrete_df.iterrows():
        c, _ = pd.factorize(row, sort=False)  # NaN→-1
        rows.append(c.astype(np.int64))
    X = np.stack(rows, axis=0)
    n = X.shape[0]
    out = np.zeros((n, n), dtype=float)

    for i in range(n):
        for j in range(i, n):
            xi, xj = X[i], X[j]
            if ignore_na:
                m = (xi >= 0) & (xj >= 0)
                xi, xj = xi[m], xj[m]
            if xi.size == 0:
                vij = np.nan
            elif i == j:
                vij = 0.0
            else:
                Ai, Aj = xi.max()+1, xj.max()+1
                cont = np.zeros((Ai, Aj), dtype=np.int64)
                np.add.at(cont, (xi, xj), 1)
                # H(X), H(Y), H(X,Y)
                Hx  = entropy(cont.sum(axis=1), base=base)
                Hy  = entropy(cont.sum(axis=0), base=base)
                Hxy = entropy(cont.ravel(),      base=base)
                # 或者用 I：mi_nats = mutual_info_score(None, None, contingency=cont)
                vij = 2*Hxy - Hx - Hy
            out[i, j] = out[j, i] = vij

    return pd.DataFrame(out, index=discrete_df.index, columns=discrete_df.index)


def compute_distance_matrix(df: pd.DataFrame, method: str, sigma: float = 1.0, bins: int = 7,
                            return_zscore: bool = True) -> pd.DataFrame:
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
        # standardized_df = zscore_standardize_rows(df)
        eudistance = pairwise_distances(df, metric="euclidean")
        return pd.DataFrame(eudistance, index=df.index, columns=df.index)
        
    elif method == "information":
        discretized_df = gaussian_discretization_fast(df, sigma=sigma, bins=bins, return_zscore=return_zscore)
        return information_distance(discretized_df)
    else:
        raise ValueError(f"未知的距离计算方法: {method}")

if __name__ == "__main__":
    df = pd.read_csv("D:\python\Relevance_System\data\statisticsData.txt",encoding="gbk",index_col=0,sep="\t")

    pd = compute_distance_matrix(df, "euclidean")
    print(pd)