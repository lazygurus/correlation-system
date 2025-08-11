import os
import numpy as np
import sys
import pandas as pd


class FileLoader:
    """
    文件加载器类，用于从 CSV/TXT 文件中读取数据，并将其转换为 numpy 矩阵和标签列表
    """
    
    def __init__(self):
        pass

    def upload(self, file_path: str):
        """
        从指定 CSV/TXT 文件路径读取数据，返回 numpy 矩阵、行标签、列标签

        :param file_path: CSV/TXT 文件路径
        :return: tuple of (numpy.ndarray, row_labels, col_labels)
        """
        try:
            # 使用 pandas 读取文件，第一列作为行标签，第一列作为行标签
            # 根据文件扩展名选择分隔符
            ext = os.path.splitext(file_path)[1].lower()
            sep = ',' if ext == '.csv' else '\t' 
            
            # 尝试用 utf-8 编码读取文件，如果失败则使用 gbk 编码
            try:
                df = pd.read_csv(file_path, sep=sep, index_col=0, header=0, engine='python', encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, sep=sep, index_col=0, header=0, engine='python', encoding='gbk')

            data = df.to_numpy()                 # 内容矩阵
            row_labels = df.index.to_list()      # 行标签
            col_labels = df.columns.to_list()    # 列标签

            return data, row_labels, col_labels
        except Exception as e:
            print(f"读取文件出错: {e}")
            return None, None, None

    def download(self, data, row_labels, col_labels, file_path):
        """
        将数据、行标签和列标签保存到指定文件

        :param data: numpy.ndarray，数据矩阵
        :param row_labels: list，行标签
        :param col_labels: list，列标签
        :param file_path: str，保存文件路径
        """
        if data is None or row_labels is None or col_labels is None:
            print("没有可下载的数据。")
            return False
        
        try:
            distance_df = pd.DataFrame(data, index=row_labels, columns=col_labels)
            if file_path.endswith(".csv"):
                distance_df.to_csv(file_path, sep=",", encoding="utf-8")
            elif file_path.endswith(".txt"):
                distance_df.to_csv(file_path, sep="\t", encoding="utf-8")
            return True
        except Exception as e:
            print(f"出现异常: {e}")
            return False


if __name__ == "__main__":
    # 测试代码
    file_path = sys.argv[1]  # 替换为你的 CSV 文件路径
    file_loader = FileLoader()
    data, row_labels, col_labels = file_loader.upload(file_path)
    if data is not None:
        print("数据矩阵:\n", data)
        print("行标签:", row_labels)
        print("列标签:", col_labels)