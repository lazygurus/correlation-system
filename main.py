import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QFileDialog
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
        
        self.resize_and_center()

    def resize_and_center(self):
        screen = QApplication.screenAt(self.pos())
        screen_geo: QRect = screen.availableGeometry()

        w = screen_geo.width() // 2
        h = screen_geo.height() // 2

        self.resize(w, h)
        self.move(
            screen_geo.x() + (screen_geo.width() - w) // 2,
            screen_geo.y() + (screen_geo.height() - h) // 2
        )


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())