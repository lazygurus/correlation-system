from PyQt5.QtGui import QShowEvent
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QFileDialog
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex

from qfluentwidgets import TableView

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import rcParams


class FileDialog(QFileDialog):
    def __init___(self, parent):
        super().__init__(parent)
        
    def showEvent(self, a0: QShowEvent) -> None:
        super().showEvent(a0)
        self.setCenter(self.parent())

    def setCenter(self, parent):
        """
        设置对话框的中心位置
        :param center: 中心点坐标 (x, y)
        """
        if not self.isVisible():
            self.adjustSize()
                
        # 以父窗口中心为目标点
        parent_center = parent.frameGeometry().center()

        # 把对话框的几何框移动到该中心
        g = self.frameGeometry()
        g.moveCenter(parent_center)

        # 防止越界到屏幕外：按父窗口所在屏幕裁剪
        screen = parent.screen() or QApplication.screenAt(parent_center) or QApplication.primaryScreen()
        sgeo = screen.availableGeometry()
        tl = g.topLeft()
        x = max(sgeo.left(),  min(tl.x(), sgeo.right()  - g.width()  + 1))
        y = max(sgeo.top(),   min(tl.y(), sgeo.bottom() - g.height() + 1))
        self.move(x, y)
    

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
    集成matplotlib的绘图组件，支持点选择、距离计算、撤销和缩放功能

    :function plotPoints: 传入包含点坐标的pandas DataFrame绘制散点图
    :function clearPlot: 清空当前绘图
    :function setTitle: 设置图表标题
    :function setAxisLabels: 设置坐标轴标签
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # 设置中文字体
        rcParams["font.family"] = "sans-serif"
        rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC"]
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
        self.hint_text = self.axes.text(
            0.01, 0.01,  # 位置（左下角，相对坐标）
            "按 Z 键撤销标注",
            fontsize=14,
            color='green',
            transform=self.axes.transAxes,  # 使用相对坐标（0-1 范围）
            verticalalignment='bottom',  # 垂直对齐方式
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)  # 白色背景框，增加可读性
        )

        # 交互功能变量初始化
        self.scatter = None  # 散点图对象
        self.coordinates = None  # 存储坐标数据
        self.names = None  # 点名称
        self.x_col = None  # x列名
        self.y_col = None  # y列名

        # 交互状态变量
        self.selected_indices = []  # 当前选中的点索引
        self.annotations = []  # 所有标注对象
        self.lines = []  # 所有连接线
        self.point_labels = []  # 点标签
        self.operations = []  # 操作历史记录

        # 绑定事件
        self.cid_pick = self.canvas.mpl_connect('pick_event', self.on_pick)
        self.cid_key = self.canvas.mpl_connect('key_press_event', self.on_key)
        self.cid_scroll = self.canvas.mpl_connect('scroll_event', self.on_scroll)

        # 确保画布获得焦点以接收键盘事件
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()

    def plotPoints(self, coordinates: pd.DataFrame, x_col=None, y_col=None,
                   color='skyblue', marker='o', size=50, alpha=0.7, label=None,
                   names=None):
        """绘制点坐标散点图，支持交互选择和距离计算"""
        if coordinates is None or not isinstance(coordinates, pd.DataFrame):
            print("数据无效，请传入有效的 pandas DataFrame")
            return

        if coordinates.empty:
            print("DataFrame 为空")
            return

        # 保存数据供交互使用
        self.coordinates = coordinates.copy()
        self.names = coordinates.index.tolist()

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

        # 保存列名
        self.x_col = x_col
        self.y_col = y_col

        try:
            # 获取 x和 y数据
            x_data = coordinates[x_col].to_numpy()
            y_data = coordinates[y_col].to_numpy()

            # 清空之前的绘图和状态
            self.clearPlot()

            # 绘制散点图，开启拾取功能
            self.scatter = self.axes.scatter(
                x_data, y_data,
                c=color, marker=marker,
                s=size, alpha=alpha,
                label=label,
                picker=True  # 开启拾取功能
            )

            # 重新设置标签和网格
            self.axes.set_xlabel(x_col)
            self.axes.set_ylabel(y_col)
            self.axes.set_title('散点图')
            self.axes.grid(True, alpha=0.3)

            # 如果有标签，显示图例
            if label:
                self.axes.legend()

            # 刷新画布
            self.canvas.draw()
            print(f"已绘制 {len(x_data)} 个点，等待交互...")

        except Exception as e:
            print(f"绘图时发生错误: {str(e)}")

    def clearPlot(self):
        """清空当前绘图"""
        self.axes.clear()
        self.scatter = None
        self.selected_indices = []
        self.annotations = []
        self.lines = []
        self.point_labels = []
        self.operations = []
        # 重置标签
        self.axes.set_xlabel(self.x_col if self.x_col else 'X坐标')
        self.axes.set_ylabel(self.y_col if self.y_col else 'Y坐标')
        self.axes.grid(True, alpha=0.3)
        # 保留提示
        self.hint_text = self.axes.text(
            0.01, 0.01,
            "按Z键撤销标注",
            fontsize=14,
            color='green',
            transform=self.axes.transAxes,
            verticalalignment='bottom',
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)
        )
        self.canvas.draw()

    def setTitle(self, title: str):
        """设置图表标题"""
        self.axes.set_title(title)
        self.canvas.draw()

    def setAxisLabels(self, x_label: str, y_label: str):
        """设置坐标轴标签"""
        self.axes.set_xlabel(x_label)
        self.axes.set_ylabel(y_label)
        self.x_col = x_label
        self.y_col = y_label
        self.canvas.draw()

    # 点击事件回调：选择点并计算距离
    def on_pick(self, event):
        # 确保我们只处理散点图的拾取事件
        if self.scatter is None or event.artist != self.scatter:
            return

        # 忽略滚轮等其他事件   mouseevent———— 1-左键  2-滚轮  3-右键
        if hasattr(event, 'mouseevent') and event.mouseevent.button != 1:
            return  # 不是左键点击，直接返回，不处理

        # 获取点击的点索引
        ind = event.ind[0]

        # 防止重复选择同一点
        if ind in self.selected_indices:
            return

        # 添加到选中列表
        self.selected_indices.append(ind)
        print(f"选中点索引: {ind}，当前选中 {len(self.selected_indices)} 个点")

        # 获取点数据
        x_data = self.coordinates[self.x_col].to_numpy()
        y_data = self.coordinates[self.y_col].to_numpy()

        # 将选中的点设为红色
        colors = ['red' if i in self.selected_indices else 'skyblue' for i in range(len(x_data))]
        self.scatter.set_color(colors)

        # 显示点信息
        label = self.axes.text(
            x_data[ind], y_data[ind],
            f"{self.names[ind]}\n({x_data[ind]:.3f},{y_data[ind]:.3f})",
            fontsize=9, color='blue', fontweight='bold'
        )
        self.point_labels.append(label)

        # 当选中2个点时，绘制连接线和距离
        if len(self.selected_indices) == 2:
            i, j = self.selected_indices

            # 计算距离
            dist = np.sqrt((x_data[i] - x_data[j]) ** 2 + (y_data[i] - y_data[j]) ** 2)

            # 绘制连接线
            line, = self.axes.plot(
                [x_data[i], x_data[j]], [y_data[i], y_data[j]],
                color='blue', linewidth=1.5
            )
            self.lines.append(line)

            # 显示距离
            mid_x = (x_data[i] + x_data[j]) / 2
            mid_y = (y_data[i] + y_data[j]) / 2
            annot = self.axes.text(
                mid_x, mid_y, f"距离: {dist:.3f}",
                color='blue', fontsize=10, fontweight='bold'
            )
            self.annotations.append(annot)

            # 记录操作历史
            self.operations.append({
                'points': self.selected_indices.copy(),
                'line': line,
                'annotation': annot,
                'labels': [self.point_labels[-2], self.point_labels[-1]]
            })

            # 重置选中状态，准备下一次选择
            self.selected_indices = []

        # 更新显示
        self.canvas.draw()

    # 键盘事件：撤销上一次操作
    def on_key(self, event):
        if event.key == 'z':  # 撤销
            if not self.operations and not self.selected_indices:
                print("没有可撤销的操作")
                return

            # 处理未完成的选择（只选了一个点）
            if self.selected_indices:
                print(f"撤销未完成的选择，清除 {len(self.selected_indices)} 个点")
                # 清除选中状态
                if self.point_labels:
                    for label in self.point_labels[-len(self.selected_indices):]:
                        label.remove()
                    del self.point_labels[-len(self.selected_indices):]

                # 恢复点颜色
                x_data = self.coordinates[self.x_col].to_numpy()
                colors = ['skyblue'] * len(x_data)
                self.scatter.set_color(colors)

                # 重置选中列表
                self.selected_indices = []
                self.canvas.draw()
                return

            # 处理已完成的操作
            if self.operations:
                last_op = self.operations.pop()
                print(f"撤销上一次操作，清除 {len(last_op['points'])} 个点的标记")

                # 移除连接线
                if last_op['line'] in self.lines:
                    last_op['line'].remove()            # 删除图像
                    self.lines.remove(last_op['line'])  # 删除内存中的线

                # 移除距离标注
                if last_op['annotation'] in self.annotations:
                    last_op['annotation'].remove()
                    self.annotations.remove(last_op['annotation'])

                # 移除点标签
                for label in last_op['labels']:
                    if label in self.point_labels:
                        label.remove()
                        self.point_labels.remove(label)

                # 恢复点颜色
                x_data = self.coordinates[self.x_col].to_numpy()
                colors = ['skyblue'] * len(x_data)
                self.scatter.set_color(colors)

                self.canvas.draw()

    # 鼠标滚轮事件：实现缩放功能
    def on_scroll(self, event):
        # 获取当前坐标轴范围
        cur_xlim = self.axes.get_xlim()
        cur_ylim = self.axes.get_ylim()

        # 获取鼠标在数据坐标系中的位置
        if event.xdata is None or event.ydata is None:
            return  # 鼠标在绘图区域外时不响应

        xdata = event.xdata
        ydata = event.ydata

        # 缩放因子
        scale_factor = 1.1
        if event.button == 'down':
            scale_factor = 1 / scale_factor

        # 计算新的坐标轴范围
        new_width = (cur_xlim[1] - cur_xlim[0]) / scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) / scale_factor

        # 计算新的起点
        new_x_start = xdata - (xdata - cur_xlim[0]) / scale_factor
        new_y_start = ydata - (ydata - cur_ylim[0]) / scale_factor

        # 设置新的范围
        self.axes.set_xlim(new_x_start, new_x_start + new_width)
        self.axes.set_ylim(new_y_start, new_y_start + new_height)

        self.canvas.draw()


# 为了确保PyQt的焦点设置生效，需要导入Qt
from PyQt5.QtCore import Qt
