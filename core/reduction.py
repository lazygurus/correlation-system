import numpy as np
import pandas as pd
from sklearn.manifold import MDS

def reduce_dimension(distance_matrix: pd.DataFrame, n_components: int = 2, random_state: int = 42) -> pd.DataFrame:
    """使用 MDS 将预计算的距离矩阵降维到低维坐标。

    Args:
        distance_matrix: 预先计算好的距离矩阵（行列索引为对象名；若首列为字符串会被设为行索引）。
        n_components: 目标维度，必须为正整数且不大于样本数。
        random_state: 随机种子；设为 None 可关闭固化。

    Returns:
        pandas.DataFrame: 低维坐标表，索引继承自距离矩阵，列为坐标维度名。

    Raises:
        TypeError: distance_matrix 不是 DataFrame，或 n_components 不是整数。
        ValueError: 矩阵为空、或 n_components 取值不合法。
    """
    if not isinstance(distance_matrix, pd.DataFrame):
        raise TypeError("distance_matrix 必须是 pandas.DataFrame。")
    if not isinstance(n_components, int):
        raise TypeError("n_components 必须为整数。")
    if distance_matrix.empty:
        raise ValueError("距离矩阵不能为空。")
    if n_components <= 0:
        raise ValueError("n_components 必须为正整数。")
    
    distance = distance_matrix.to_numpy()
    mds = MDS(
        n_components=n_components,
        dissimilarity="precomputed",  # 直接使用距离矩阵
        random_state=random_state
    )
    coords = mds.fit_transform(distance)
    return pd.DataFrame(coords, index=distance_matrix.index, columns=['x', 'y'])