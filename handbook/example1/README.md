# 旅行手册生成器

这是一个Python项目，用于根据预定义的行程数据动态生成一份图文并茂的PDF旅行手册。

## 功能

- **动态行程**: 所有行程数据都在 `generate_travel_handbook.py` 文件中以结构化形式存储，方便修改和扩展。
- **PDF生成**: 使用 `reportlab` 库将行程数据渲染成专业的PDF文档。
- **自定义字体**: 支持中文字体，确保内容正确显示。
- **图片集成**:
    - **背景图片**: 自动为每个页面添加背景图，并可调整透明度以保证文字可读性。
    - **每日地图**: 为每日行程预留地图区域，并能自动将图片按比例缩放并居中放置。
- **图片格式转换**: 包含一个辅助脚本 `convert_image.py`，用于将PNG等格式的图片转换为PDF兼容的JPG格式。

## 项目结构

```
.
├── materials/
│   ├── generate_travel_handbook.py  # 主程序：生成PDF手册
│   ├── convert_image.py             # 辅助工具：转换图片格式
│   ├── background.jpg               # (示例) 背景图片
│   ├── map_day1.jpg                 # (示例) 第一天的地图
│   ├── map_day2.jpg                 # (示例) 第二天的地图
│   └── ...                          # 其他地图图片
├── requirements.txt                 # 项目依赖
└── README.md                        # 本说明文档
```

## 如何使用

### 1. 环境准备

首先，确保您的系统中安装了Python。然后，在项目根目录下，通过以下命令安装所需的依赖库：

```bash
pip install
```
reportlab
Pillow


### 2. 准备素材

- **背景图**: 准备一张您喜欢的图片作为手册的背景，将其命名为 `background.jpg` 并放入 `materials` 文件夹。
- **地图**: 使用地图应用（如百度地图、高德地图）截取每日行程的路线图或景点图。将它们分别命名为 `map_day1.jpg`, `map_day2.jpg`, ..., `map_day8.jpg`，然后放入 `materials` 文件夹。
  > **注意**: 如果您的图片是PNG或其他格式，请先使用 `convert_image.py` 脚本进行转换。例如，要转换 `map_day1.png`，请在 `convert_image.py` 中修改文件名，然后运行 `python materials/convert_image.py`。

### 3. 自定义行程

打开 `materials/generate_travel_handbook.py` 文件，您可以直接修改 `itinerary` 列表中的内容，包括：
- 日期、标题、每日总览
- 详细的时间线安排
- 地图区域的提示文字

### 4. 生成手册

完成以上步骤后，运行主程序来生成PDF：

```bash
python materials/generate_travel_handbook.py
```

执行成功后，您会在 `materials` 文件夹中找到最终的 `黑龙江全景深度游手册.pdf` 文件。

## 自定义扩展

- **背景透明度**: 在 `generate_travel_handbook.py` 中，您可以修改 `c.setFillColorRGB(1, 1, 1, alpha=0.6)` 这一行中的 `alpha` 值（范围0.0到1.0）来调整背景图片的明暗程度。
- **字体**: 如果需要更换字体，请修改 `FONT_PATH` 变量，指向您系统中的字体文件路径。
