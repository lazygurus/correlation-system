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
        self.discretized_data = None
        self.eudistance = None
        self.infodistance = None
        self.coordinates = None

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
        # 标签栏切换
        self.tabBar.tabCloseRequested.connect(lambda index: self.controllers.close_tab(index))
        self.stackedWidget.currentChanged.connect(lambda index: self.tabBar.setCurrentIndex(index))
        # 导入按钮
        self.uploadDataButton.clicked.connect(lambda: self.controllers.upload_data("data"))
        self.uploadEuDistButton.clicked.connect(lambda: self.controllers.upload_data("eudistance"))
        self.uploadInfoDistButton.clicked.connect(lambda: self.controllers.upload_data("infodistance"))
        self.uploadCoordButton.clicked.connect(lambda: self.controllers.upload_data("coordinate"))
        # 离散化按钮
        self.discreteDataButton.clicked.connect(lambda: self.controllers.discretize(self.data))
        # 计算距离按钮
        self.calDistButton.clicked.connect(
            lambda: self.controllers.compute_distance(
                self.data,
                euclidean=self.euDistSwitch.isChecked(),
                information=self.infoDistSwitch.isChecked()
            )
        )
        # 降维按钮
        self.reduceDimButton.clicked.connect(lambda: self.controllers.reduce(self.eudistance))
        self.reduceDimButton.clicked.connect(lambda: self.controllers.reduce(self.infodistance))
        # 绘图按钮
        self.drawButton.clicked.connect(lambda: self.controllers.plot_coordinates(self.coordinates))
        # 导出按钮
        self.downloadEuDistButton.clicked.connect(lambda: self.controllers.download_data("eudistance"))
        self.downloadInfoDistButton.clicked.connect(lambda: self.controllers.download_data("infodistance"))
        self.downloadCoordButton.clicked.connect(lambda: self.controllers.download_data("coordinate"))
        self.downloadDiscreteDataButton.clicked.connect(lambda: self.controllers.download_data("discretized_data"))