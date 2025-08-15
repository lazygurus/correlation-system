from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex
from qfluentwidgets import TableView
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import rcParams
import numpy as np


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


class PlotWidget(QWidget):
    """
    集成matplotlib的绘图组件，可以绘制点坐标散点图
    
    :function plotPoints: 传入包含点坐标的 pandas DataFrame 可以绘制散点图
    :function clearPlot: 清空当前绘图
    :function setTitle: 设置图表标题
    :function setAxisLabels: 设置坐标轴标签
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        rcParams["font.family"] = "sans-serif"
        rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC"]  # 任选其一系统已安装即可
        rcParams["axes.unicode_minus"] = False  # 负号正常显示
                
        # 创建matplotlib图形和画布
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(111)
        
        # 设置布局
        self.vlayout = QVBoxLayout(self)
        self.vlayout.addWidget(self.canvas)
        self.setLayout(self.vlayout)
        
        # 设置默认样式
        self.figure.patch.set_facecolor('white')
        self.axes.grid(True, alpha=0.3)
        self.axes.set_axisbelow(True)
        
        # 初始化默认标签
        self.axes.set_xlabel('X坐标')
        self.axes.set_ylabel('Y坐标')
        self.axes.set_title('散点图')
        
    def plotPoints(self, coordinates: pd.DataFrame, x_col=None, y_col=None, 
                   color='blue', marker='o', size=50, alpha=0.7, label=None):
        """
        绘制点坐标散点图

        :param coordinates: 包含坐标数据的 pandas DataFrame
        :param x_col: x坐标列名，如果为None则使用第一列
        :param y_col: y坐标列名，如果为None则使用第二列
        :param color: 点的颜色
        :param marker: 点的标记样式
        :param size: 点的大小
        :param alpha: 透明度
        :param label: 图例标签
        """
        if coordinates is None or not isinstance(coordinates, pd.DataFrame):
            print("数据无效，请传入有效的 pandas DataFrame")
            return

        if coordinates.empty:
            print("DataFrame 为空")
            return
            
        # 确定 x和 y列
        columns = coordinates.columns.tolist()
        if len(columns) < 2:
            print("DataFrame 至少需要两列数据作为x和y坐标")
            return
            
        if x_col is None:
            x_col = columns[0]
        if y_col is None:
            y_col = columns[1]
            
        if x_col not in columns or y_col not in columns:
            print(f"指定的列名不存在。可用列: {columns}")
            return
            
        try:
            # 获取 x和 y数据
            x_data = coordinates[x_col]
            y_data = coordinates[y_col]

            # 清空之前的绘图
            self.axes.clear()
            
            # 绘制散点图
            scatter = self.axes.scatter(x_data, y_data, c=color, marker=marker, 
                                      s=size, alpha=alpha, label=label)
            
            print("YES")
            
            # 重新设置标签和网格
            self.axes.set_xlabel(x_col)
            self.axes.set_ylabel(y_col)
            self.axes.set_title('散点图')
            self.axes.grid(True, alpha=0.3)
            self.axes.set_axisbelow(True)
            
            # 如果有标签，显示图例
            if label:
                self.axes.legend()
            
            # 刷新画布
            self.canvas.draw()
            
        except Exception as e:
            print(f"绘图时发生错误: {str(e)}")
            
    def addPoints(self, dataframe: pd.DataFrame, x_col=None, y_col=None,
                  color='red', marker='s', size=50, alpha=0.7, label=None):
        """
        在现有图上添加新的点（不清空之前的绘图）
        参数同plotPoints方法
        """
        if dataframe is None or not isinstance(dataframe, pd.DataFrame):
            print("数据无效，请传入有效的 pandas DataFrame")
            return
            
        if dataframe.empty:
            print("DataFrame 为空")
            return
            
        # 确定x和y列
        columns = dataframe.columns.tolist()
        if len(columns) < 2:
            print("DataFrame 至少需要两列数据作为x和y坐标")
            return
            
        if x_col is None:
            x_col = columns[0]
        if y_col is None:
            y_col = columns[1]
            
        if x_col not in columns or y_col not in columns:
            print(f"指定的列名不存在。可用列: {columns}")
            return
            
        try:
            # 获取x和y数据
            x_data = dataframe[x_col]
            y_data = dataframe[y_col]
            
            # 添加散点图（不清空之前的内容）
            scatter = self.axes.scatter(x_data, y_data, c=color, marker=marker,
                                      s=size, alpha=alpha, label=label)
            
            # 如果有标签，更新图例
            if label:
                self.axes.legend()
                
            # 自动调整坐标轴范围
            self.axes.relim()
            self.axes.autoscale_view()
            
            # 刷新画布
            self.canvas.draw()
            
        except Exception as e:
            print(f"添加点时发生错误: {str(e)}")
    
    def clearPlot(self):
        """清空当前绘图"""
        self.axes.clear()
        # 重新设置默认样式
        self.axes.grid(True, alpha=0.3)
        self.axes.set_axisbelow(True)
        self.axes.set_xlabel('X坐标')
        self.axes.set_ylabel('Y坐标')
        self.axes.set_title('散点图')
        self.canvas.draw()
        
    def setTitle(self, title):
        """设置图表标题"""
        self.axes.set_title(title)
        self.canvas.draw()
        
    def setAxisLabels(self, xlabel, ylabel):
        """设置坐标轴标签"""
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)
        self.canvas.draw()
        
    def savePlot(self, filename, dpi=300, bbox_inches='tight'):
        """
        保存图表到文件
        :param filename: 保存的文件名
        :param dpi: 图像分辨率
        :param bbox_inches: 边界框设置
        """
        try:
            self.figure.savefig(filename, dpi=dpi, bbox_inches=bbox_inches)
            print(f"图表已保存到: {filename}")
        except Exception as e:
            print(f"保存图表时发生错误: {str(e)}")
            
    def setPlotStyle(self, style='default'):
        """
        设置绘图样式
        :param style: matplotlib样式名称，如 'seaborn', 'ggplot', 'dark_background' 等
        """
        try:
            plt.style.use(style)
            self.canvas.draw()
        except Exception as e:
            print(f"设置样式时发生错误: {str(e)}")