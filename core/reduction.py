import numpy as np
import pandas as pd
from sklearn.manifold import MDS

def reduce_dimension(distance_matrix, n_components: int = 2, random_state: int = 42) -> pd.DataFrame:
    """
    使用 MDS 将距离矩阵降维到二维
    distance_matrix: 预先计算好的距离矩阵
    n_components: 降维目标维度，默认 2
    random_state: 随机种子，保证结果可复现
    """
    first_col = distance_matrix.iloc[:, 0]
    if first_col.dtype == 'object' or isinstance(first_col.iloc[0], str):
        distance_matrix = distance_matrix.set_index(distance_matrix.columns[0])  # 把第一列作为索引

    if distance_matrix is None or distance_matrix.empty:
        print("距离矩阵为空，无法进行降维。")
        return pd.DataFrame()
    
    distance = distance_matrix.to_numpy()
    mds = MDS(
        n_components=n_components,
        dissimilarity="precomputed",  # 直接使用距离矩阵
        random_state=random_state
    )
    coords = mds.fit_transform(distance)
    return pd.DataFrame(coords, index=distance_matrix.index, columns=['x', 'y'])