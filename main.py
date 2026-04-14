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
    解析markdown文件内容，处理标题、加粗和红/绿颜色标签
    支持标签：[r]红色文字[/r], [g]绿色文字[/g]
    :param file_path: markdown文件路径
    :return: 包含行信息的列表，每行包含多个文本片段(segments)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    parsed_content = []
    # 定义颜色常量
    COLOR_MAP = {
        'r': (255, 0, 0),    # 红色
        'g': (0, 255, 0),    # 绿色
        'default': None      # 使用全局字体颜色
    }

    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 提取标题信息
        header_match = re.match(r'^(#+)\s+(.*)$', line)
        level = 0
        text_content = line
        is_header = False
        if header_match:
            level = len(header_match.group(1))
            text_content = header_match.group(2)
            is_header = True

        # 处理加粗 (统一去掉标记，因为我们目前按行/片段处理加粗)
        # 这里为了简单，如果行内含 ** 或 __，则该行片段默认为加粗
        is_bold_line = ('**' in text_content) or ('__' in text_content)
        text_content = text_content.replace('**', '').replace('__', '')

        # 解析颜色标签 [r]...[/r] 和 [g]...[/g]
        # 使用正则表达式分割文本并提取颜色信息
        # 这是一个简单的状态机解析或正则分割
        segments = []
        pattern = r'\[([rg])\](.*?)\[/\1\]'
        
        last_pos = 0
        for match in re.finditer(pattern, text_content):
            # 添加匹配前的普通文本
            if match.start() > last_pos:
                segments.append({
                    'text': text_content[last_pos:match.start()],
                    'color_key': 'default',
                    'bold': is_bold_line
                })
            
            # 添加带颜色的文本
            segments.append({
                'text': match.group(2),
                'color_key': match.group(1),
                'bold': is_bold_line or is_header # 标题默认加粗
            })
            last_pos = match.end()
            
        # 添加剩余文本
        if last_pos < len(text_content):
            segments.append({
                'text': text_content[last_pos:],
                'color_key': 'default',
                'bold': is_bold_line or is_header
            })

        if not segments: # 处理没有颜色标签的情况
             segments.append({
                'text': text_content,
                'color_key': 'default',
                'bold': is_bold_line or is_header
            })

        parsed_content.append({
            'type': 'header' if is_header else 'text',
            'level': level,
            'segments': segments
        })
            
    return parsed_content

def create_scrolling_text_video(input_file, output_file, video_width=1280, video_height=720, fps=30, scroll_speed=2, base_font_size=48, font_color=(255, 255, 255), bg_color=(0, 0, 0), text_align='center', margin=50):
    """
    创建从下往上垂直滚动字幕的视频，支持Markdown和颜色标签
    :param input_file: 输入的txt或md文件路径
    :param output_file: 输出的视频文件路径
    :param video_width: 视频宽度
    :param video_height: 视频高度
    :param fps: 视频帧率
    :param scroll_speed: 滚动速度（像素/帧）
    :param base_font_size: 基础字体大小
    :param font_color: 默认字体颜色
    :param bg_color: 背景颜色
    :param text_align: 对齐方式 ('left', 'center', 'right')
    :param margin: 左右边距（仅对左/右对齐有效）
    """
    COLOR_MAP = {
        'r': (255, 0, 0),    # 红色
        'g': (0, 255, 0),    # 绿色
        'default': font_color
    }

    if input_file.endswith('.md'):
        content_items = parse_markdown(input_file)
    else:
        text_lines = read_text_file(input_file)
        content_items = [{
            'type': 'text', 
            'level': 0, 
            'segments': [{'text': line, 'color_key': 'default', 'bold': False}]
        } for line in text_lines]

    if not content_items:
        print("输入文件内容为空")
        return
    
    font_paths = {
        'regular': "C:/Windows/Fonts/msyh.ttc",
        'bold': "C:/Windows/Fonts/msyhbd.ttc",
    }
    fallback_fonts = ["C:/Windows/Fonts/simhei.ttf", "C:/Windows/Fonts/simsun.ttc"]

    def get_font(is_bold, size):
        path = font_paths['bold'] if is_bold else font_paths['regular']
        if not os.path.exists(path):
            for f_path in fallback_fonts:
                if os.path.exists(f_path):
                    path = f_path
                    break
        try:
            return ImageFont.truetype(path, size)
        except:
            return ImageFont.load_default()

    line_data = []
    total_text_height = 0
    
    for item in content_items:
        if item['type'] == 'header':
            size = int(base_font_size * (1.5 - (item['level'] - 1) * 0.1))
            size = max(size, base_font_size)
        else:
            size = base_font_size
            
        line_height = size + 20
        
        # 处理这一行的所有片段
        segments_data = []
        line_width = 0
        # 预先计算这一行的总宽度
        temp_img = Image.new('RGB', (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        
        for seg in item['segments']:
            font = get_font(seg['bold'], size)
            w = temp_draw.textlength(seg['text'], font=font)
            segments_data.append({
                'text': seg['text'],
                'font': font,
                'color': COLOR_MAP.get(seg['color_key'], font_color),
                'width': w
            })
            line_width += w

        line_data.append({
            'segments': segments_data,
            'line_width': line_width,
            'height': line_height,
            'y_offset': total_text_height
        })
        total_text_height += line_height
    
    total_duration = (video_height + total_text_height) / (scroll_speed * fps)
    
    def make_frame(t):
        img = Image.new('RGB', (video_width, video_height), bg_color)
        draw = ImageDraw.Draw(img)
        current_scroll = int(t * fps * scroll_speed)
        
        for line in line_data:
            y = video_height - current_scroll + line['y_offset']
            
            if -line['height'] < y < video_height:
                # 根据对齐方式计算起始位置
                if text_align == 'left':
                    current_x = margin
                elif text_align == 'right':
                    current_x = video_width - line['line_width'] - margin
                else:  # center
                    current_x = (video_width - line['line_width']) // 2
                
                for seg in line['segments']:
                    draw.text((current_x, y), seg['text'], font=seg['font'], fill=seg['color'])
                    current_x += seg['width']
        
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

    # 示例 2: MD 文件 (居中对齐)
    # input_md_file = "test_markdown.md"
    # output_md_video = "test_markdown_center.mp4"
    # create_scrolling_text_video(input_md_file, output_md_video, text_align='center')

    # # 示例 3: MD 文件 (左对齐)
    # output_md_video_left = "test_markdown_left.mp4"
    # create_scrolling_text_video(input_md_file, output_md_video_left, text_align='left', margin=100)
    
    input_md_file = "2026热门高校计算机考研复试线.md"
    output_md_video_left = "profess.mp4"
    create_scrolling_text_video(input_md_file, output_md_video_left, text_align='left', margin=100)