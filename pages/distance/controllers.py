import pandas as pd
import numpy as np

from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.QtCore import Qt

from core.loader import FileLoader
from pages.distance.widgets import tableWidget


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

    def upload_data(self, type: str):
        """
        加载文件数据到表格组件
        
        :param type: str, 数据类型: 1.原始数据 2.距离数据 3.坐标
        """
        allowed_type = {"data", "distance", "coordinate"}
        if type not in allowed_type:
            print("数据类型不合理")
            return False
        
        tab_title = {"data": "原始数据", "distance": "距离", "coordinate": "坐标"}  # 不同类型数据对应的 tab 栏标题
        file_path, _ = QFileDialog.getOpenFileName(self.parent, "选择文件", "", "CSV Files (*.csv);;Text Files (*.txt)")
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

    def download_data(self, type:str):
        """
        将表格数据保存到文件
        """
        allowed_type = {"data", "distance", "coordinate"}
        if type not in allowed_type:
            print("数据类型不合理")
            return False
        
        # 获取当前类型的数据
        data = getattr(self.parent, type)
        if data is None:
            print("没有可下载的数据。")
            return False

        file_path, _ = QFileDialog.getSaveFileName(self.parent, "保存文件", "", "CSV Files (*.csv);;Text Files (*.txt)")
        if file_path:
            result = self.loader.download(data, file_path)
            return result
        else:
            print("未选择保存路径。")
            return False