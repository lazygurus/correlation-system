import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from reduction import reduce_dimension
from distance import compute_distance_matrix

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 从文件读取数据
csv_file = "D:\python\Relevance_System\data\statisticsData.txt"  # 替换成你的文件路径
df = pd.read_csv(csv_file, encoding='gbk', sep='\t')
distance_matrix = compute_distance_matrix(df, "euclidean")
matrix = reduce_dimension(distance_matrix)

# 提取数据
names = matrix.index.tolist()
x = matrix['x'].to_numpy()
y = matrix['y'].to_numpy()

# 绘制散点图
fig, ax = plt.subplots(figsize=(10, 8))
# 初始散点为天蓝色，保存散点集合用于后续颜色修改
sc = ax.scatter(x, y, s=50, color='skyblue', picker=5)  # picker=5 表示点击半径
ax.set_title("带距离计算和缩放功能的交互式散点图")
ax.set_xlabel("X轴")
ax.set_ylabel("Y轴")
ax.grid(True)

# 交互功能变量
selected_points = []  # 当前选中的点索引
operation_history = []  # 存储完整的操作记录
current_operation = {}  # 当前正在构建的操作
original_colors = ['skyblue'] * len(x)  # 保存所有点的原始颜色


# 点击事件回调：选择点并计算距离
def on_pick(event):
    global current_operation
    ind = event.ind[0]  # 点击的点索引

    # 如果当前没有正在构建的操作，创建一个新操作
    if not current_operation:
        current_operation = {
            'points': [],
            'texts': [],
            'line': None,
            'annotation': None,
            'original_colors': []  # 保存点的原始颜色，用于撤销
        }

    # 记录选中的点及其原始颜色
    selected_points.append(ind)
    current_operation['points'].append(ind)
    current_operation['original_colors'].append(original_colors[ind])

    # 将选中的点设为红色
    original_colors[ind] = 'red'
    sc.set_color(original_colors)

    # 显示点信息文本
    txt = ax.text(x[ind], y[ind], f"{names[ind]}\n({x[ind]:.3f},{y[ind]:.3f})",
                  fontsize=9, color='blue', fontweight='bold')
    current_operation['texts'].append(txt)

    # 当选中2个点时，完成当前操作
    if len(selected_points) == 2:
        i, j = selected_points
        # 计算距离
        dist = np.sqrt((x[i] - x[j]) ** 2 + (y[i] - y[j]) ** 2)

        # 绘制蓝色线段（修改为蓝色）
        line, = ax.plot([x[i], x[j]], [y[i], y[j]], color='blue', linewidth=1.5)
        current_operation['line'] = line

        # 绘制距离文本
        mid_x = (x[i] + x[j]) / 2
        mid_y = (y[i] + y[j]) / 2
        annot = ax.text(mid_x, mid_y, f"{dist:.3f}", color='blue',  # 文本也改为蓝色以匹配线段
                        fontsize=10, fontweight='bold')
        current_operation['annotation'] = annot

        # 将完成的操作添加到历史记录
        operation_history.append(current_operation)
        # 重置状态
        selected_points.clear()
        current_operation = {}

    fig.canvas.draw()


# 键盘事件：撤销上一次操作
def on_key(event):
    global current_operation, selected_points
    if event.key == 'z':  # 撤销
        # 处理未完成的操作（如果有选中但未完成的点）
        if current_operation:
            # 恢复点的原始颜色
            for i, ind in enumerate(current_operation['points']):
                original_colors[ind] = current_operation['original_colors'][i]
            sc.set_color(original_colors)

            # 移除当前操作中已添加的文本
            for txt in current_operation['texts']:
                txt.remove()

            # 重置状态
            current_operation = {}
            selected_points.clear()
            fig.canvas.draw()
            print("撤销未完成的选择")
            return

        # 处理已完成的操作
        if operation_history:
            # 获取最后一次操作
            last_op = operation_history.pop()

            # 恢复点的原始颜色
            for i, ind in enumerate(last_op['points']):
                original_colors[ind] = last_op['original_colors'][i]
            sc.set_color(original_colors)

            # 移除线段
            if last_op['line']:
                last_op['line'].remove()

            # 移除距离标注
            if last_op['annotation']:
                last_op['annotation'].remove()

            # 移除点信息文本
            for txt in last_op['texts']:
                txt.remove()

            fig.canvas.draw()
            print("撤销上一次测距")
        else:
            print("没有可撤销的操作")


# 鼠标滚轮事件：实现缩放功能
def on_scroll(event):
    # 获取当前坐标轴范围
    cur_xlim = ax.get_xlim()
    cur_ylim = ax.get_ylim()

    # 获取鼠标在数据坐标系中的位置
    xdata = event.xdata
    ydata = event.ydata

    # 缩放因子
    scale_factor = 1.1  # 放大倍数
    if event.button == 'down':  # 滚轮向下滚动，缩小
        scale_factor = 1 / scale_factor

    # 计算新的坐标轴范围
    new_width = (cur_xlim[1] - cur_xlim[0]) / scale_factor
    new_height = (cur_ylim[1] - cur_ylim[0]) / scale_factor

    # 计算新的中心点（基于鼠标位置）
    new_x_start = xdata - (xdata - cur_xlim[0]) / scale_factor
    new_y_start = ydata - (ydata - cur_ylim[0]) / scale_factor

    # 设置新的坐标轴范围
    ax.set_xlim(new_x_start, new_x_start + new_width)
    ax.set_ylim(new_y_start, new_y_start + new_height)

    fig.canvas.draw()


# 绑定事件
fig.canvas.mpl_connect('pick_event', on_pick)
fig.canvas.mpl_connect('key_press_event', on_key)
fig.canvas.mpl_connect('scroll_event', on_scroll)  # 绑定滚轮事件

plt.show()
