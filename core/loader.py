import os
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
        :return: pandas.DataFrame，包含数据的 DataFrame
        """
        try:
            # 使用 pandas 读取文件，第一列作为行标签，第一列作为行标签
            # 根据文件扩展名选择分隔符
            extension = os.path.splitext(file_path)[1].lower()
            seperator = ',' if extension == '.csv' else '\t'

            # 尝试用 utf-8 编码读取文件，如果失败则使用 gbk 编码
            try:
                df = pd.read_csv(file_path, sep=seperator, index_col=0, header=0, engine='python', encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, sep=seperator, index_col=0, header=0, engine='python', encoding='gbk')

            return df
        except Exception as e:
            print(f"读取文件出错: {e}")
            return None

    def download(self, df: pd.DataFrame, file_path: str):
        """
        将数据、行标签和列标签保存到指定文件

        :param df: pandas.DataFrame，包含数据的 DataFrame
        :param file_path: str，保存文件路径
        """
        if df.empty:
            print("没有可下载的数据。")
            return False

        try:
            if file_path.endswith(".csv"):
                df.to_csv(file_path, sep=",", encoding="utf-8")
            elif file_path.endswith(".txt"):
                df.to_csv(file_path, sep="\t", encoding="utf-8")
            return True
        except Exception as e:
            print(f"出现异常: {e}")
            return False