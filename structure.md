# 项目结构说明

## 目录结构

```
relation/
│
├── main.py                      # 程序入口文件
├── README.md                    # 项目说明文档
├── requirements.txt             # Python 依赖包列表
├── structure.md                 # 项目结构文档
├── .gitignore                   # Git 忽略文件配置
│
├── config/                      # 应用配置模块
│   └── settings.py              # 应用配置（常量、颜色、样式）
│
├── ui/                          # UI 文件及自动生成文件
│   ├── main_window.ui           # Qt Designer 设计文件
│   └── main_window_ui.py        # 由 .ui 转换的 py 文件（pyuic5 生成）
│
├── pages/                       # 各个功能页面模块
│   └── distance/                # 距离计算页面
│       ├── page.py              # 页面主逻辑
│       ├── widgets.py           # 子组件封装
│       └── controllers.py       # 控制器逻辑
│
├── core/                        # 核心功能模块（计算与数据处理）
│   ├── distance.py              # 欧式/信息距离计算
│   ├── reduction.py             # 降维算法封装
│   ├── visualizer.py            # 调用 matplotlib 进行绘图
│   └── load.py                  # 数据加载
│
├── assets/                      # 图标、样式、字体等资源
│   └── icons/                   # 图标文件
│
├── sytle/                       # 样式文件（注：原拼写保持）
│   └── theme.qss                # Qt 样式表文件
│
└── utils/                       # 工具模块
    └── helpers.py               # 公共辅助函数（如异常处理、提示框等）
```

## 模块说明

### 主要文件

- **main.py**: 应用程序的主入口，包含 MainWindow 类和应用启动逻辑

### 核心模块

#### pages/distance/
距离计算和可视化功能的核心模块：
- `page.py`: 距离分析页面的主要逻辑
- `widgets.py`: 自定义 UI 组件
- `controllers.py`: 业务逻辑控制器

#### core/
核心算法和数据处理模块：
- `distance.py`: 实现各种距离计算算法
- `reduction.py`: 数据降维算法实现
- `visualizer.py`: 数据可视化逻辑
- `load.py`: 数据文件加载和处理

#### config/
应用配置管理：
- `settings.py`: 应用程序的配置常量和设置

### 资源和样式

#### assets/
静态资源文件：
- `icons/`: 应用程序图标和界面图标

#### sytle/
界面样式文件：
- `theme.qss`: Qt 样式表，定义应用程序的视觉风格

#### utils/
通用工具函数：
- `helpers.py`: 公共辅助函数，如错误处理、用户提示等

## 开发指南

### 添加新功能页面
1. 在 `pages/` 目录下创建新的子目录
2. 按照 `distance/` 模块的结构创建相应文件
3. 在 `main.py` 中注册新页面

### 添加新的核心算法
1. 在 `core/` 目录下创建相应的 Python 模块
2. 实现算法逻辑并提供统一的接口
3. 在相关页面中调用算法

### 自定义样式
1. 修改 `sytle/theme.qss` 文件
2. 在 `config/settings.py` 中添加样式相关的配置