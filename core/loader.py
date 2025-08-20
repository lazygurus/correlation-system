import os
import pandas as pd


def upload(path: str) -> pd.DataFrame:
    """读取 CSV/TXT 并返回 DataFrame。

    Args:
        path: 文件路径。

    Returns:
        pandas.DataFrame: 读取的数据表（首列为索引）。

    Raises:
        FileNotFoundError: 文件不存在。
        ValueError: 路径为空/后缀不支持/内容为空。
        UnicodeDecodeError: 尝试的编码均无法解码。
    """
    # 路径检查
    if not isinstance(path, str) or not path.strip():
        raise ValueError("文件路径不能为空")
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    
    # 获取文件后缀名，根据后缀选择分隔符
    ext = os.path.splitext(path)[1].lower()
    if ext not in (".csv", ".txt"):
        raise ValueError(f"不支持 {ext} 文件格式")
    sep = "," if ext == ".csv" else "\t"
    
    # 逐个编码尝试读取
    last_decode_err = None
    for enc in ("utf-8", "gbk"):
        try:
            df = pd.read_csv(
                path,
                sep=sep,
                index_col=0,
                header=0,
                engine="python",
                encoding=enc,
            )
        except UnicodeDecodeError as e:
            last_decode_err = e
        except pd.errors.EmptyDataError as e:
            raise ValueError(f"文件内容为空") from e
        else:
            return df
    
    raise last_decode_err


def download(df: pd.DataFrame, path: str) -> bool:
    """将 DataFrame 保存为 CSV/TXT（utf-8）。

    Args:
        df: 待保存数据表。
        path: 目标路径。

    Returns:
        bool: 保存成功返回 True。

    Raises:
        TypeError: df 不是 DataFrame。
        ValueError: df 为空、路径为空/后缀不支持。
    """
    # 参数检查
    if not isinstance(df, pd.DataFrame):
        raise TypeError("传入的数据必须是 pandas DataFrame")
    if df.empty:
        raise ValueError("没有可保存的数据（DataFrame 为空）")
    if not isinstance(path, str) or not path.strip():
        raise ValueError("保存路径不能为空")

    # 后缀名检查
    ext = os.path.splitext(path)[1].lower()
    if ext not in (".csv", ".txt"):
        raise ValueError("仅支持保存为 .csv 或 .txt")

    # 保存 df
    sep = "," if ext == ".csv" else "\t"
    df.to_csv(path, sep=sep, encoding="utf-8")
    return True
