from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from qfluentwidgets import TableView


class tableWidget(QWidget):
    """
    自定义表格视图组件，使用 FluentWidgets 的 TableView
    :function addItem: 传入 data, row_labels, col_labels 可以将数据添加到表格上
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
        
    def addItem(self, data, row_labels, col_labels):
        if data is None or row_labels is None or col_labels is None:
            print("数据无效")
            return

        rows, cols = data.shape
        model = QStandardItemModel(rows, cols)

        # 设置表格数据项
        for i in range(rows):
            for j in range(cols):
                item = QStandardItem(str(data[i, j]))
                item.setTextAlignment(Qt.AlignCenter)         # 水平居中显示
                item.setEditable(False)                       # 禁止编辑（可选）
                model.setItem(i, j, item)

        # 设置列头（Horizontal Header）
        model.setHorizontalHeaderLabels([str(label) for label in col_labels])

        # 设置行头（Vertical Header）
        model.setVerticalHeaderLabels([str(label) for label in row_labels])

        # 应用模型
        self.table.setModel(model)