# Txt2ScrollVideo

一个简单高效的 Python 工具，可以将 `.txt` 或 `.md` (Markdown) 文件转换为带有垂直滚动字幕效果的 MP4 视频。

## 功能特点

- **Markdown 支持**: 自动识别多级标题（# 到 ######）和加粗文本（** 或 __）。
- **动态样式**: 不同层级的标题会自动调整字号，并应用加粗样式。
- **自动忽略视频**: 预置 `.gitignore` 配置，生成的 `.mp4` 文件不会被误提交。
- **中文友好**: 默认支持微软雅黑等 Windows 中文字体。

## 安装

1. 确保已安装 Python 3.11+。
2. 安装项目依赖：

```bash
pip install -r requirements.txt
```

## 快速使用

### 1. 准备输入文件

你可以准备一个普通的文本文件 `example.txt`：

```text
第一行文字
第二行文字
...
```

或者一个 Markdown 文件 `example.md`：

```markdown
# 这是一个标题
## 这是一个副标题
这是**加粗**的正文。
```

### 2. 运行脚本

修改 [main.py](file:///d:/ProjectTRAE/dev_daily/Txt2ScrollVideo/main.py) 中的输入文件路径，然后运行：

```bash
python main.py
```

### 3. 代码调用示例

```python
from main import create_scrolling_text_video

# 转换为视频
create_scrolling_text_video(
    input_file="test_markdown.md", 
    output_file="output_video.mp4",
    video_width=1280,   # 视频宽度
    video_height=720,   # 视频高度
    fps=30,             # 帧率
    scroll_speed=2      # 滚动速度（像素/帧）
)
```

## 项目结构

- [main.py](file:///d:/ProjectTRAE/dev_daily/Txt2ScrollVideo/main.py): 核心逻辑，包含解析 Markdown 和生成视频的代码。
- [requirements.txt](file:///d:/ProjectTRAE/dev_daily/Txt2ScrollVideo/requirements.txt): 项目所需的 Python 依赖包。
- [.gitignore](file:///d:/ProjectTRAE/dev_daily/Txt2ScrollVideo/.gitignore): 排除生成的视频文件和其他临时文件。
- [test_markdown.md](file:///d:/ProjectTRAE/dev_daily/Txt2ScrollVideo/test_markdown.md): 用于功能测试的 Markdown 示例文件。

## 注意事项

- 本工具目前主要适配 Windows 系统的字体路径（如 `C:/Windows/Fonts/msyh.ttc`）。
- 视频生成时长取决于文本的总长度和滚动速度。
