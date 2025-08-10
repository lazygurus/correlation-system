import numpy as np
import sys
import pandas as pd

def loader(file_path: str):
    """
    从指定 CSV/TXT 文件路径读取数据，返回 numpy 矩阵、行标签、列标签

    :param file_path: CSV/TXT 文件路径
    :return: tuple of (numpy.ndarray, row_labels, col_labels)
    """
    try:
        # 使用 pandas 读取文件，第一列作为行标签，第一列作为行标签
        # 使用 utf-8 编码读取，如果失败则尝试 gbk 编码
        try:
            df = pd.read_csv(file_path, sep=",", index_col=0, header=0, engine='python', encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, sep="\\s+", index_col=0, header=0, engine='python', encoding='gbk')

        data = df.to_numpy()                 # 内容矩阵
        row_labels = df.index.to_list()      # 行标签
        col_labels = df.columns.to_list()    # 列标签

        return data, row_labels, col_labels
    except Exception as e:
        print(f"读取文件出错: {e}")
        return None, None, None
    

if __name__ == "__main__":
    # 测试代码
    file_path = sys.argv[1]  # 替换为你的 CSV 文件路径
    data, row_labels, col_labels = loader(file_path)
    if data is not None:
        print("数据矩阵:\n", data)
        print("行标签:", row_labels)
        print("列标签:", col_labels)