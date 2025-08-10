import pandas as pd
import numpy as np

from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.QtCore import Qt

from core.loader import uploader, downloader
from pages.distance.widgets import tableWidget


def add_tab(parent, widget, object_name: str, text: str, icon: str = "assets/icon/book.png"):
    """
    添加标签页到堆叠组件和标签栏
    :param parent: 父组件，包含堆叠组件和标签栏
    :param widget: 要添加的组件
    :param object_name: 组件的对象名称
    :param text: 标签栏显示的文本
    :param icon: 标签栏显示的图标路径
    """
    widget.setObjectName(object_name)
    parent.stackedWidget.addWidget(widget)
    parent.tabBar.addTab(
        routeKey=object_name,
        text=text,
        icon=icon,
        onClick=lambda: parent.stackedWidget.setCurrentWidget(widget)
    )
    parent.stackedWidget.setCurrentWidget(widget)


def close_tab(parent, index: int):
    """
    关闭指定索引的标签页
    :param parent: 父组件，包含堆叠组件和标签栏
    :param index: 要关闭的标签页索引
    """
    item = parent.tabBar.tabItem(index)
    widget = parent.findChild(QWidget, item.routeKey())
    parent.stackedWidget.removeWidget(widget)
    parent.tabBar.removeTab(index)
    widget.deleteLater()


def upload_data(parent, object_name: str, text: str, icon: str = "assets/icon/book.png"):
    """
    加载文件数据到表格组件
    :param parent: 父组件，包含堆叠组件和标签栏
    :param object_name: 表格的对象名称
    :param text: 标签栏显示的文本
    :param icon: 标签栏显示的图标路径
    """
    file_path, _ = QFileDialog.getOpenFileName(parent, "选择文件", "", "CSV Files (*.csv);;Text Files (*.txt)")
    if file_path:
        # 读取文件数据
        parent.data, parent.rows, parent.cols = uploader(file_path)
        if parent.data is not None:
            # 添加表格到堆叠组件
            table = tableWidget()
            table.addItem(parent.data, parent.rows, parent.cols)
            add_tab(parent, table, object_name=object_name, text=text, icon=icon)
            return True
        else: 
            print("加载数据失败，请检查文件格式或内容。")
            return False
    else:
        print("未选择文件。")
        return False

    
def download_data(parent):
    """
    将表格数据保存到文件
    :param parent: 父组件，包含堆叠组件和标签栏
    """
    if not hasattr(parent, 'data') or parent.data is None:
        print("没有可下载的数据。")
        return False
    
    file_path, _ = QFileDialog.getSaveFileName(parent, "保存文件", "", "CSV Files (*.csv);;Text Files (*.txt)")
    if file_path:
        result = downloader(parent.data, parent.rows, parent.cols, file_path)
        return result
    else:
        print("未选择保存路径。")
        return False
