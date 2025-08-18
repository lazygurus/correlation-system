import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QFileDialog, QStyle
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QStandardItem, QStandardItemModel

from qfluentwidgets import FluentWindow, FluentIcon, TableView
from pages.distance.page import DistanceInterface


class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("相关性分析系统")

        self.distance_Interface = DistanceInterface(self.stackedWidget)
        self.addSubInterface(self.distance_Interface, FluentIcon.SETTING, "距离可视化")
        
        self.resize_and_center(0.7, 0.8)

    def resize_and_center(self, width_frac=0.8, height_frac=0.8):
        """
        设置窗口大小并居中

        :param width_frac: 窗口宽度占屏幕可用区域的比例
        :param height_frac: 窗口高度占屏幕可用区域的比例
        """
        screen = QApplication.screenAt(self.pos())
        screen_geo: QRect = screen.availableGeometry()

        # 设置窗口大小，最小宽度为300，最小高度为200
        tw = max(300, int(screen_geo.width()  * width_frac))
        th = max(200, int(screen_geo.height() * height_frac))
        self.resize(tw, th)

        rect = QStyle.alignedRect(Qt.LeftToRight, Qt.AlignCenter, self.size(), screen_geo)
        self.move(rect.topLeft())


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())