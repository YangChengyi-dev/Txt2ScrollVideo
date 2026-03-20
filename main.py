import sys
import os

from moviepy import VideoClip
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def read_text_file(file_path):
    """
    读取txt文件内容
    :param file_path: txt文件路径
    :return: 文本内容列表
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # 去除每行末尾的换行符
    lines = [line.strip() for line in lines]
    # 过滤空行
    lines = [line for line in lines if line]
    return lines

import re

def parse_markdown(file_path):
    """
    解析markdown文件内容，处理标题和加粗
    :param file_path: markdown文件路径
    :return: 包含文本内容、类型和样式的列表
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    parsed_content = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 匹配标题 (# 标题)
        header_match = re.match(r'^(#+)\s+(.*)$', line)
        if header_match:
            level = len(header_match.group(1))
            text = header_match.group(2)
            # 处理标题中的加粗
            text = text.replace('**', '').replace('__', '')
            parsed_content.append({
                'type': 'header',
                'level': level,
                'text': text,
                'bold': True
            })
            continue

        # 处理正文中的加粗 (**文本** 或 __文本__)
        # 简单处理：如果整行或部分包含加粗，目前逻辑将其作为一行处理
        # 这里的逻辑可以根据需求调整，当前为了滚动效果，我们按行处理
        is_bold = False
        if ('**' in line and line.count('**') >= 2) or ('__' in line and line.count('__') >= 2):
            is_bold = True
            line = line.replace('**', '').replace('__', '')
            
        parsed_content.append({
            'type': 'text',
            'level': 0,
            'text': line,
            'bold': is_bold
        })
            
    return parsed_content

def create_scrolling_text_video(input_file, output_file, video_width=1280, video_height=720, fps=30, scroll_speed=2, base_font_size=48, font_color=(255, 255, 255), bg_color=(0, 0, 0)):
    """
    创建从下往上垂直滚动字幕的视频，支持Markdown
    :param input_file: 输入的txt或md文件路径
    :param output_file: 输出的视频文件路径
    ...
    """
    # 根据文件后缀决定解析方式
    if input_file.endswith('.md'):
        content_items = parse_markdown(input_file)
    else:
        # 兼容原有的txt逻辑
        text_lines = read_text_file(input_file)
        content_items = [{'type': 'text', 'level': 0, 'text': line, 'bold': False} for line in text_lines]

    if not content_items:
        print("输入文件内容为空")
        return
    
    # 字体路径准备
    font_paths = {
        'regular': "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
        'bold': "C:/Windows/Fonts/msyhbd.ttc",   # 微软雅黑加粗
    }
    # 备选字体
    fallback_fonts = ["C:/Windows/Fonts/simhei.ttf", "C:/Windows/Fonts/simsun.ttc"]

    def get_font(is_bold, size):
        path = font_paths['bold'] if is_bold else font_paths['regular']
        if not os.path.exists(path):
            # 尝试备选
            for f_path in fallback_fonts:
                if os.path.exists(f_path):
                    path = f_path
                    break
        try:
            return ImageFont.truetype(path, size)
        except:
            return ImageFont.load_default()

    # 计算每一行的高度和样式
    line_data = []
    total_text_height = 0
    
    for item in content_items:
        # 根据标题层级计算字号
        if item['type'] == 'header':
            size = int(base_font_size * (1.5 - (item['level'] - 1) * 0.1))
            size = max(size, base_font_size)
        else:
            size = base_font_size
            
        font = get_font(item['bold'], size)
        line_height = size + 20 # 增加一些行间距
        
        line_data.append({
            'text': item['text'],
            'font': font,
            'height': line_height,
            'y_offset': total_text_height
        })
        total_text_height += line_height
    
    # 计算视频总帧数
    total_duration = (video_height + total_text_height) / (scroll_speed * fps)
    
    def make_frame(t):
        img = Image.new('RGB', (video_width, video_height), bg_color)
        draw = ImageDraw.Draw(img)
        
        current_scroll = int(t * fps * scroll_speed)
        
        for data in line_data:
            # 每一行的起始y坐标
            y = video_height - current_scroll + data['y_offset']
            
            # 优化：只绘制在屏幕内的行
            if -data['height'] < y < video_height:
                text_width = draw.textlength(data['text'], font=data['font'])
                x = (video_width - text_width) // 2
                draw.text((x, y), data['text'], font=data['font'], fill=font_color)
        
        return np.array(img)
    
    video_clip = VideoClip(make_frame, duration=total_duration)
    video_clip = video_clip.with_fps(fps)
    video_clip.write_videofile(output_file, codec='libx264', audio=False)
    print(f"视频已生成：{output_file}")

if __name__ == "__main__":
    # 示例 1: TXT 文件
    # input_text_file = "NIE.txt"
    # output_video_file = "NIE_scrolling_text_video.mp4"
    # create_scrolling_text_video(input_text_file, output_video_file)

    # 示例 2: MD 文件
    input_md_file = "test_markdown.md"
    output_md_video = "test_markdown_video.mp4"
    create_scrolling_text_video(input_md_file, output_md_video)
