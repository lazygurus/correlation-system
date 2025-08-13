from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

from qfluentwidgets import BodyLabel

from ui.Ui_distance_page import Ui_distance_page
from pages.distance.controllers import Controllers


class DistanceInterface(QWidget, Ui_distance_page):
    """
    距离可视化页面，继承自 QWidget 和 Ui_distance_page
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # 实例化控制器
        self.controllers = Controllers(self)
        
        # 设初始数据为 None
        self.data = None
        self.distance = None
        self.coordinate = None

        # 初始化 UI
        self.setupUi(self)
        self.setObjectName("distance_page")
        self.init_page()
        self.set_style()
        
        # 设置槽函数
        self.set_Slot()
    
    def init_page(self):
        """
        初始化页面，设置标题和欢迎信息"""
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        label = BodyLabel("欢迎使用相关性分析系统")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        widget.setLayout(layout)
        self.controllers.add_tab(widget, "home", "主页", icon='assets/icon/book.png')

    def set_style(self):
        """ 
        设置页面样式
        """
        # 设置滚动区域样式
        self.scrollArea.setStyleSheet("QScrollArea { border: none; }")
        
        # 设置标签样式
        self.tabBar.setMovable(True)
        self.tabBar.setTabMaximumWidth(150)
        self.tabBar.setTabShadowEnabled(False)
        self.tabBar.setTabSelectedBackgroundColor(QColor(255, 255, 255, 125), QColor(255, 255, 255, 50))
        
    def set_Slot(self):
        """
        设置槽函数
        """
        self.tabBar.tabCloseRequested.connect(lambda index: self.controllers.close_tab(index))
        self.stackedWidget.currentChanged.connect(lambda index: self.tabBar.setCurrentIndex(index))
        self.uploadFileButton.clicked.connect(lambda: self.controllers.upload_data("data"))
        self.uploadDistButton.clicked.connect(lambda: self.controllers.upload_data("distance"))
        self.downloadDistButton.clicked.connect(lambda: self.controllers.download_data("distance"))