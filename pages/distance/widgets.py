from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex
from qfluentwidgets import TableView
import pandas as pd


class DataFrameModel(QAbstractTableModel):
    """
    基于 QAbstractTableModel 的自定义数据模型，用于将 pandas DataFrame 转换为表格视图
    """
    def __init__(self, df: pd.DataFrame, parent=None):
        super().__init__(parent)
        self._df = df if df is not None else pd.DataFrame()

    def rowCount(self, parent=QModelIndex()):
        """返回行数"""
        return 0 if parent.isValid() else len(self._df)

    def columnCount(self, parent=QModelIndex()):
        """返回列数"""
        return 0 if parent.isValid() else len(self._df.columns)

    def data(self, index, role=Qt.DisplayRole):
        """返回指定索引的数据"""
        if not index.isValid():
            return None
            
        row = index.row()
        col = index.column()

        if role == Qt.DisplayRole:
            try:
                value = self._df.iat[row, col]
                # 处理不同的数据类型
                if pd.isna(value):
                    return "NaN"
                elif isinstance(value, float):
                    return f"{value:.6f}"  # 保留6位小数
                else:
                    return str(value)
            except Exception as e:
                return "Error"
        
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """设置表头数据"""
        if role == Qt.DisplayRole:
            try:
                if orientation == Qt.Horizontal:
                    return str(self._df.columns[section])
                else:  # Qt.Vertical(行头)
                    return str(self._df.index[section])
            except Exception:
                pass
        return None
    
    def setDataFrame(self, df):
        """更新 DataFrame 数据"""
        self.beginResetModel()
        self._df = df if df is not None else pd.DataFrame()
        self.endResetModel()
    
    def getDataFrame(self):
        """获取当前的 DataFrame"""
        return self._df.copy() if not self._df.empty else pd.DataFrame()


class tableWidget(QWidget):
    """
    自定义表格视图组件，使用 FluentWidgets 的 TableView
    :function addItem: 传入 pandas DataFrame 可以将数据添加到表格上
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 创建空白表格组件
        self.table = TableView(self)
        self.table.setBorderVisible(True)       # 显示边框
        self.table.setBorderRadius(8)           # 设置圆角
        self.table.setWordWrap(False)           # 禁用自动换行
        
        # 设置布局
        self.vlayout = QVBoxLayout(self)
        self.vlayout.addWidget(self.table)
        self.setLayout(self.vlayout)
        
    def addItem(self, dataframe: pd.DataFrame):
        """
        添加 pandas DataFrame 数据到表格
        :param dataframe: pandas DataFrame 对象
        """
        if dataframe is None or not isinstance(dataframe, pd.DataFrame):
            print("数据无效，请传入有效的 pandas DataFrame")
            return

        if dataframe.empty:
            print("DataFrame 为空")
            return

        # 如果表格已经有模型，更新数据；否则创建新模型
        current_model = self.table.model()
        if current_model is not None and isinstance(current_model, DataFrameModel):
            current_model.setDataFrame(dataframe)
        else:
            # 使用自定义的 DataFrameModel
            model = DataFrameModel(dataframe)
            self.table.setModel(model)
    
    def clearData(self):
        """清空表格数据"""
        current_model = self.table.model()
        if current_model is not None and isinstance(current_model, DataFrameModel):
            current_model.setDataFrame(pd.DataFrame())
    
    def getCurrentDataFrame(self):
        """获取当前表格中的数据"""
        current_model = self.table.model()
        if current_model is not None and isinstance(current_model, DataFrameModel):
            return current_model.getDataFrame()
        return pd.DataFrame()