import numpy as np
from sklearn.manifold import MDS


def reduce_dimension(distance_matrix: np.ndarray, n_components: int = 2, random_state: int = 42) -> np.ndarray:
    """
    使用 MDS 将距离矩阵降维到二维
    distance_matrix: 预先计算好的距离矩阵
    n_components: 降维目标维度，默认 2
    random_state: 随机种子，保证结果可复现
    """
    mds = MDS(
        n_components=n_components,
        dissimilarity="precomputed",  # 直接使用距离矩阵
        random_state=random_state
    )
    coords = mds.fit_transform(distance_matrix)
    return coords
