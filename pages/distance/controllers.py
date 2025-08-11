import pandas as pd
import numpy as np

from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.QtCore import Qt

from core.loader import uploader, downloader
from pages.distance.widgets import tableWidget


class Controllers:
    def __init__(self, parent):
        self.parent = parent
        
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


    def upload_data(self, object_name: str, text: str, icon: str = "assets/icon/book.png"):
        """
        加载文件数据到表格组件
        :param object_name: 表格的对象名称
        :param text: 标签栏显示的文本
        :param icon: 标签栏显示的图标路径
        """
        file_path, _ = QFileDialog.getOpenFileName(self.parent, "选择文件", "", "CSV Files (*.csv);;Text Files (*.txt)")
        if file_path:
            # 读取文件数据
            self.parent.data, self.parent.rows, self.parent.cols = uploader(file_path)
            if self.parent.data is not None:
                # 添加表格到堆叠组件
                table = tableWidget()
                table.addItem(self.parent.data, self.parent.rows, self.parent.cols)
                self.add_tab(table, object_name=object_name, text=text, icon=icon)
                return True
            else: 
                print("加载数据失败，请检查文件格式或内容。")
                return False
        else:
            print("未选择文件。")
            return False


    def download_data(self):
        """
        将表格数据保存到文件
        """
        if not hasattr(self.parent, 'data') or self.parent.data is None:
            print("没有可下载的数据。")
            return False

        file_path, _ = QFileDialog.getSaveFileName(self.parent, "保存文件", "", "CSV Files (*.csv);;Text Files (*.txt)")
        if file_path:
            result = downloader(self.parent.data, self.parent.rows, self.parent.cols, file_path)
            return result
        else:
            print("未选择保存路径。")
            return False
