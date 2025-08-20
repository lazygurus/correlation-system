import numpy as np
import pandas as pd
from sklearn.metrics import pairwise_distances
from scipy.stats import entropy


def zscore_standardize_rows(df: pd.DataFrame) -> pd.DataFrame:
    """按行做 Z-score 标准化。

    Args:
        df: 随机变量 DataFrame。

    Returns:
        pandas.DataFrame: 与输入同形的标准化数据。

    Raises:
        TypeError: df 不是 DataFrame。
        ValueError: df 为空。
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df 必须是 pandas.DataFrame。")
    if df.empty:
        raise ValueError("DataFrame 为空。")
    
    row_mean = df.mean(axis=1).values.reshape(-1, 1)  # 每行均值
    row_std = (df.std(axis=1) + 1e-12).values.reshape(-1, 1)  # 每行标准差
    return (df - row_mean) / row_std


def gaussian_discretization(df: pd.DataFrame, sigma: float = 1.0, bins: int = 7,
                                 return_zscore: bool = True) -> pd.DataFrame:
    """按行基于高斯核的自适应离散化（向量化实现）。

    Args:
        df: 数值型 DataFrame，行=随机变量，列=样本。
        sigma: 高斯核标准差，必须为正。
        bins: 离散等级数量，建议 ≥ 3。
        return_zscore: True 返回 z-score 的中心；False 返回原值空间的中心。

    Returns:
        pandas.DataFrame: 离散化后的 DataFrame，索引与列名与输入一致。

    Raises:
        TypeError: df 不是 DataFrame，或 bins 不是整数。
        ValueError: df 为空/非数值/含 NaN，sigma ≤ 0，或 bins < 2。
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df 必须是 pandas.DataFrame。")
    if not isinstance(bins, int):
        raise TypeError("bins 必须为整数。")
    if df.empty:
        raise ValueError("DataFrame 为空。")
    if sigma <= 0:
        raise ValueError("sigma 必须为正。")
    if bins < 2:
        raise ValueError("bins 必须 ≥ 2。")
    
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
    """计算变分信息距离（Variation of Information, VI）。

    对每一行分别做编码（`pd.factorize`），再两两构建列联表并计算
    :math:`VI(X,Y) = 2H(X,Y) - H(X) - H(Y)`。

    Args:
        discrete_df: 离散化后的 DataFrame（每行一个随机变量，列为样本）。
        base: 熵的对数底，默认 2 表示以 bit 为单位。
        ignore_na: True 时在两变量的“共同观测”上计算（同时非缺失）。

    Returns:
        pandas.DataFrame: 对称的 VI 距离矩阵，主对角为 0。

    Raises:
        TypeError: 输入不是 DataFrame。
        ValueError: DataFrame 为空或 base ≤ 0。
    """
    if not isinstance(discrete_df, pd.DataFrame):
        raise TypeError("discrete_df 必须是 pandas.DataFrame。")
    if discrete_df.empty:
        raise ValueError("离散化数据为空。")
    if base <= 0:
        raise ValueError("base 必须为正。")
    
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


def compute_distance_matrix(df: pd.DataFrame, method: str, sigma: float = 1.0, bins: int = 13,
                            return_zscore: bool = True) -> pd.DataFrame:
    """根据方法计算距离矩阵。

    - euclidean：计算欧氏距离；
    - information：先做高斯离散化，再计算 VI 距离。

    Args:
        df: 行=随机变量、列=样本的 DataFrame。若首列为字符串，会被设为行索引。
        method: 距离类型，``"euclidean"`` 或 ``"information"``。
        sigma: 高斯离散化的标准差，仅在 ``information`` 有效，需为正。
        bins: 离散等级数量，仅在 ``information`` 有效，需为整数且 ≥ 2。
        return_zscore: ``information`` 路径下是否返回 z-score 中心。

    Returns:
        pandas.DataFrame: 带行列标签的方阵距离矩阵。

    Raises:
        TypeError: df 不是 DataFrame，或 bins 不是整数。
        ValueError: df 为空。
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df 必须是 pandas.DataFrame。")
    if df.empty:
        raise ValueError("DataFrame 为空，无法计算距离。")
    
    # 先检查第一列是否为字符串，如果是的话，就将其转换为行索引
    first_col = df.iloc[:, 0]
    if first_col.dtype == 'object' or isinstance(first_col.iloc[0], str):
        df = df.set_index(df.columns[0])  # 把第一列作为索引

    if method == "euclidean":
        # standardized_df = zscore_standardize_rows(df)
        eudistance = pairwise_distances(df, metric="euclidean")
        return pd.DataFrame(eudistance, index=df.index, columns=df.index)
        
    elif method == "information":
        discretized_df = gaussian_discretization(df, sigma=sigma, bins=bins, return_zscore=return_zscore)
        return information_distance(discretized_df)
    else:
        raise ValueError(f"未知的距离计算方法: {method}")