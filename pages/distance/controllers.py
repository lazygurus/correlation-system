import pandas as pd
import numpy as np

from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt

from qfluentwidgets import InfoBar, InfoBarPosition

from core.loader import upload, download
from core.distance import compute_distance_matrix, gaussian_discretization
from core.reduction import reduce_dimension
from pages.distance.widgets import tableWidget, PlotWidget, FileDialog


class Controllers:
    def __init__(self, parent):
        self.parent = parent
        
    def _notify(self, kind: str, title: str, content: str, *, duration: int = 2400) -> None:
        """显示消息条（右上角）。

        Args:
            kind: "success" | "error" | "warning" | "info"。
            title: 标题。
            content: 详细内容。
            duration: 自动消失时间（毫秒）。
        """
        fn = {
            "success": InfoBar.success,
            "error": InfoBar.error,
            "warning": InfoBar.warning,
            "info": InfoBar.info,
        }.get(kind, InfoBar.info)
        
        # 位置默认右上角
        fn(
            title=title, 
            content=content, 
            duration=duration,
            position=InfoBarPosition.TOP_RIGHT, 
            parent=self.parent
        )

    def add_tab(self, widget, object_name: str, text: str, icon: str = "assets/icon/book.png"):
        """添加标签页到堆叠组件和标签栏。

        Args:
            widget: 要添加的组件（已构建好）。
            object_name: 组件的对象名称（用于路由与查找）。
            text: 标签栏显示的文本。
            icon: 标签栏显示的图标路径。
        """
        try:
            widget.setObjectName(object_name)
            self.parent.stackedWidget.addWidget(widget)
            self.parent.tabBar.addTab(
                routeKey=object_name,
                text=text,
                icon=icon,
                onClick=lambda: self.parent.stackedWidget.setCurrentWidget(widget),
            )
            self.parent.stackedWidget.setCurrentWidget(widget)
        except Exception as e:
            self._notify("error", "界面错误", f"添加标签页失败：{e}")

    def close_tab(self, index: int):
        """关闭指定索引的标签页。

        Args:
            index: 要关闭的标签页索引。
        """
        try:
            item = self.parent.tabBar.tabItem(index)
            widget = self.parent.findChild(QWidget, item.routeKey())
            self.parent.stackedWidget.removeWidget(widget)
            self.parent.tabBar.removeTab(index)
            widget.deleteLater()
        except Exception as e:
            self._notify("error", "界面错误", f"关闭标签页失败：{e}")

    # 导入功能
    def upload_data(self, type: str):
        """加载文件数据到表格组件。

        Args:
            type: 数据类型枚举："data"｜"eudistance"｜"infodistance"｜"coordinates"。

        Returns:
            bool: 成功返回 True；用户取消或失败返回 False。
        """
        allowed_type = {"data", "eudistance", "infodistance", "coordinates"}
        if type not in allowed_type:
            self._notify("warning", "参数异常", f"不支持的数据类型：{type}")
            return False
        
        # 不同类型数据所对应的 tab 题目
        titles = {
            "data": "原始数据", 
            "eudistance": "欧氏距离", 
            "infodistance": "信息距离", 
            "coordinates": "坐标"
        }
        
        file_path, _ = FileDialog.getOpenFileName(
            self.parent, "选择文件", "", "CSV Files (*.csv);;Text Files (*.txt)"
        )
        
        # 正常分支：用户取消
        if not file_path:
            self._notify("info", "已取消", "未选择任何文件")
            return False  

        try:
            df = upload(file_path)
        except (FileNotFoundError, UnicodeDecodeError, ValueError) as e:
            self._notify("error", "导入失败", str(e))
            return False

        table = tableWidget()
        table.addItem(df)
        setattr(self.parent, type, df)
        self.add_tab(table, type, titles[type], icon="assets/icon/book.png")
        self._notify("success", "导入成功", f"已成功导入{titles[type]}")
        return True

    # 导出功能
    def download_data(self, type:str):
        """将表格数据保存到文件。

        Args:
            dtype: "eudistance"｜"infodistance"｜"coordinates"｜"discretized_data"。

        Returns:
            bool: 成功 True；用户取消或失败 False。
        """
        allowed_type = {"eudistance", "infodistance", "coordinates", "discretized_data"}
        if type not in allowed_type:
            self._notify("warning", "参数异常", f"不支持的数据类型：{type}")
            return False
        
        titles = {
            "eudistance": "欧氏距离", 
            "infodistance": "信息距离", 
            "coordinates": "坐标",
            "discretized_data": "离散化数据"
        }
        
        # 获取当前类型的数据
        data = getattr(self.parent, type)
        if data.empty:
            self._notify("warning", "数据异常", f"{titles[type]}为空。")
            return False

        path, _ = FileDialog.getSaveFileName(self.parent, "保存文件", "", "CSV Files (*.csv);;Text Files (*.txt)")
        if not path:
            self._notify("info", "已取消", "未选择保存路径")
            return False

        try:
            download(data, path)
        except (TypeError, ValueError) as e:
            self._notify("error", "保存失败", str(e))
        else:
            self._notify("success", "保存成功", f"已保存到：{path}")
            return True
        return False
    
    # 离散化
    def discretize(self, data: pd.DataFrame):
        """对数据进行高斯离散化并展示在新标签页。

        Args:
            data: 原始数值型 DataFrame。

        Returns:
            bool: 成功 True；失败 False。
        """
        if data is None or data.empty:
            self._notify("warning", "数据为空", "无法离散化。")
            return False

        # 进行高斯离散化
        try:
            disc = gaussian_discretization(data)
        except (TypeError, ValueError) as e:
            self._notify("error", "离散化失败", str(e))
            return False

        self.parent.discretized_data = disc
        table = tableWidget()
        table.addItem(disc)
        self.add_tab(table, "discretized_data", "离散化数据", icon="assets/icon/book.png")
        self._notify("success", "离散化完成", "已生成离散化表格。")
        return True

    # 计算距离
    def compute_distance(self, data: pd.DataFrame, euclidean: bool = False, information: bool = False):
        """计算距离矩阵并展示。

        Args:
            data: 原始数据 DataFrame。
            euclidean: 是否计算欧氏距离。
            information: 是否计算信息距离。

        Returns:
            bool: 成功 True；失败 False。
        """
        if data.empty:
            self._notify("warning", "数据为空", "无法计算距离矩阵。")
            return False
        if not euclidean and not information:
            self._notify("warning", "未选择方法", "请至少选择一种距离计算方式。")
            return False

        if euclidean:
            try:
                eudist = compute_distance_matrix(data, method="euclidean")
            except (TypeError, ValueError) as e:
                self._notify("error", "欧氏距离失败", str(e))
                return False
            self.parent.eudistance = eudist
            table = tableWidget()
            table.addItem(eudist)
            self.add_tab(table, "eudistance", "欧氏距离", icon="assets/icon/book.png")
            self._notify("success", "计算完成", "欧氏距离已生成。")

        if information:
            try:
                infodist = compute_distance_matrix(data, method="information")
            except (TypeError, ValueError) as e:
                self._notify("error", "信息距离失败", str(e))
                return False
            self.parent.infodistance = infodist
            table = tableWidget()
            table.addItem(infodist)
            self.add_tab(table, "infodistance", "信息距离", icon="assets/icon/book.png")
            self._notify("success", "计算完成", "信息距离已生成。")

        return True
    
    # 降维
    def reduce(self, distance: pd.DataFrame):
        """使用 MDS 将距离矩阵降维为坐标并展示。

        Args:
            distance: 预计算的距离矩阵（方阵、非负、主对角≈0）。

        Returns:
            bool: 成功 True；失败 False。
        """
        if distance.empty:
            self._notify("warning", "数据为空", "无法降维。")
            return False

        try:
            coords = reduce_dimension(distance)
        except (TypeError, ValueError) as e:
            self._notify("error", "降维失败", str(e))
            return False

        self.parent.coordinates = coords
        table = tableWidget()
        table.addItem(coords)
        self.add_tab(table, "coordinates", "坐标", icon="assets/icon/book.png")
        self._notify("success", "降维完成", "已生成二维坐标。")
        return True

    # 绘图
    def plot_coordinates(self, coordinates: pd.DataFrame):
        """绘制坐标点到新标签页。

        Args:
            coordinates: 坐标 DataFrame（至少两列）。
        
        Returns:
            bool: 成功 True；失败 False。
        """
        if coordinates.empty:
            self._notify("warning", "数据异常", "没有可绘制的坐标。")
            return False

        try:
            plot_widget = PlotWidget()
            plot_widget.plotPoints(coordinates)
            self.add_tab(plot_widget, "plot", "坐标图", icon="assets/icon/book.png")
            self._notify("success", "绘图完成", "坐标图已生成。")
        except Exception as e:
            self._notify("error", "绘图失败", str(e))
            return False

        return True