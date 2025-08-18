import pandas as pd
import numpy as np

from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.QtCore import Qt

from core.loader import FileLoader
from core.distance import compute_distance_matrix, gaussian_discretization_fast
from core.reduction import reduce_dimension
from pages.distance.widgets import tableWidget, PlotWidget, FileDialog


class Controllers:
    def __init__(self, parent):
        self.parent = parent
        self.loader = FileLoader()
        
    def add_tab(self, widget, object_name: str, text: str, icon: str = "assets/icon/book.png"):
        """
        添加标签页到堆叠组件和标签栏
        
        :param widget: 要添加的组件
        :param object_name: 组件的对象名称
        :param text: 标签栏显示的文本
        :param icon: 标签栏显示的图标路径
        """
        widget.setObjectName(object_name)
        self.parent.stackedWidget.addWidget(widget)
        self.parent.tabBar.addTab(
            routeKey=object_name,
            text=text,
            icon=icon,
            onClick=lambda: self.parent.stackedWidget.setCurrentWidget(widget)
        )
        self.parent.stackedWidget.setCurrentWidget(widget)

    def close_tab(self, index: int):
        """
        关闭指定索引的标签页
        
        :param index: 要关闭的标签页索引
        """
        item = self.parent.tabBar.tabItem(index)
        widget = self.parent.findChild(QWidget, item.routeKey())
        self.parent.stackedWidget.removeWidget(widget)
        self.parent.tabBar.removeTab(index)
        widget.deleteLater()

    # 导入功能
    def upload_data(self, type: str):
        """
        加载文件数据到表格组件

        :param type: str, 数据类型: 1.原始数据 2.欧氏距离数据 3.信息距离数据 4.坐标
        """
        allowed_type = {"data", "eudistance", "infodistance", "coordinates"}
        if type not in allowed_type:
            print("数据类型不合理")
            return False

        tab_title = {"data": "原始数据", "eudistance": "欧氏距离", "infodistance": "信息距离", "coordinates": "坐标"}  # 不同类型数据对应的 tab 栏标题
        file_path, _ = FileDialog.getOpenFileName(self.parent, "选择文件", "", "CSV Files (*.csv);;Text Files (*.txt)")
        if file_path:
            # 读取文件数据
            data = self.loader.upload(file_path)
            if data is not None:
                # 添加表格到堆叠组件
                table = tableWidget()
                table.addItem(data)
                setattr(self.parent, type, data)  # 保存数据到距离页面
                self.add_tab(table, type, tab_title[type], icon="assets/icon/book.png")
                return True
            else: 
                print("加载数据失败，请检查文件格式或内容。")
                return False
        else:
            print("未选择文件。")
            return False

    # 导出功能
    def download_data(self, type:str):
        """
        将表格数据保存到文件
        """
        allowed_type = {"eudistance", "infodistance", "coordinates", "discretized_data"}
        if type not in allowed_type:
            print(f"不支持的数据: {type}")
            return False
        
        # 获取当前类型的数据
        data = getattr(self.parent, type)
        if data is None:
            print(f"{type} 数据为空，无法下载。")
            return False

        file_path, _ = FileDialog.getSaveFileName(self.parent, "保存文件", "", "CSV Files (*.csv);;Text Files (*.txt)")
        if file_path:
            result = self.loader.download(data, file_path)
            return result
        else:
            print("未选择保存路径。")
            return False
    
    # 离散化
    def discretize(self, data):
        """
        对数据进行高斯离散化
        
        :param data: pandas DataFrame，包含数据
        """
        if data is None or data.empty:
            print("数据为空，无法进行离散化。")
            return False

        # 进行高斯离散化
        discretized_data = gaussian_discretization_fast(data)
        self.parent.discretized_data = discretized_data  # 保存离散化后的数据到页面
        table = tableWidget()
        table.addItem(discretized_data)
        self.add_tab(table, "discretized_data", "离散化数据", icon="assets/icon/book.png")
        return True

    # 计算距离
    def compute_distance(self, data, euclidean: bool = False, information: bool = False):
        """
        计算数据的距离矩阵
        
        :param data: pandas DataFrame，包含数据
        :return: 距离矩阵
        """
        if data is None or data.empty:
            print("数据为空，无法计算距离矩阵。")
            return False
        
        if not euclidean and not information:
            print("请至少选择一种距离计算方式。")
            return False
        
        # 计算欧氏距离矩阵
        if euclidean:
            eudist = compute_distance_matrix(data, method="euclidean")
            self.parent.eudistance = eudist  # 保存欧氏距离矩阵到页面
            table = tableWidget()
            table.addItem(eudist)
            self.add_tab(table, "eudistance", "欧氏距离", icon="assets/icon/book.png")
            return True

        if information:
            # 计算信息距离矩阵
            infodist = compute_distance_matrix(data, method="information")
            self.parent.infodistance = infodist  # 保存信息距离矩阵到页面
            table = tableWidget()
            table.addItem(infodist)
            self.add_tab(table, "infodistance", "信息距离", icon="assets/icon/book.png")
            return True

        return False
    
    # 降维
    def reduce(self, distance):
        """
        使用 MDS 将距离矩阵降维到二维

        :param distance: 预先计算好的距离矩阵
        """
        if distance is None or distance.empty:
            print("距离矩阵为空，无法进行降维。")
            return False
        
        # 降维并保存
        coords = reduce_dimension(distance)
        self.parent.coordinates = coords
        
        # 添加标签页
        table = tableWidget()
        table.addItem(coords)
        self.add_tab(table, "coordinates", "坐标", icon="assets/icon/book.png")

    # 绘图
    def plot_coordinates(self, coordinates):
        """
        绘制坐标点

        :param coordinates: pandas DataFrame，包含坐标数据
        """
        if coordinates is None or not isinstance(coordinates, pd.DataFrame):
            print("坐标数据无效")
            return

        if coordinates.empty:
            print("坐标数据为空")
            return

        # 创建绘图组件
        plot_widget = PlotWidget()
        plot_widget.plotPoints(coordinates)
        self.add_tab(plot_widget, "plot", "坐标图", icon="assets/icon/book.png")