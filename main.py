import sys
import os
# 添加用户Python库路径
sys.path.append(os.path.expanduser('~') + '\AppData\Roaming\Python\Python311\site-packages')

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

def create_scrolling_text_video(text_file, output_file, video_width=1280, video_height=720, fps=30, scroll_speed=2, font_size=48, font_color=(255, 255, 255), bg_color=(0, 0, 0)):
    """
    创建从下往上垂直滚动字幕的视频
    :param text_file: 输入的txt文件路径
    :param output_file: 输出的视频文件路径
    :param video_width: 视频宽度
    :param video_height: 视频高度
    :param fps: 视频帧率
    :param scroll_speed: 滚动速度（像素/帧）
    :param font_size: 字体大小
    :param font_color: 字体颜色（RGB）
    :param bg_color: 背景颜色（RGB）
    """
    # 读取文本内容
    text_lines = read_text_file(text_file)
    if not text_lines:
        print("文本文件为空")
        return
    
    # 计算文本总高度
    line_height = font_size + 10  # 行高（字体大小+间距）
    total_text_height = len(text_lines) * line_height
    
    # 计算视频总帧数
    # 视频总时长 = (视频高度 + 文本总高度) / 滚动速度
    total_duration = (video_height + total_text_height) / (scroll_speed * fps)
    total_frames = int(total_duration * fps)
    
    # 创建空白背景
    def make_frame(t):
        # 创建空白图像
        img = Image.new('RGB', (video_width, video_height), bg_color)
        draw = ImageDraw.Draw(img)
        
        # 尝试使用不同的中文字体
        font_paths = [
            "C:/Windows/Fonts/simhei.ttf",  # 黑体
            "C:/Windows/Fonts/simsun.ttc",  # 宋体
            "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
        ]
        
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    break
                except:
                    continue
        
        if font is None:
            # 如果没有找到合适的中文字体，使用默认字体
            font = ImageFont.load_default()
        
        # 计算当前滚动位置
        current_pos = int(t * fps * scroll_speed)
        
        # 绘制每一行文字
        for i, line in enumerate(text_lines):
            # 计算当前行的Y坐标
            y = video_height - current_pos + i * line_height
            
            # 只有当文字在视频范围内时才绘制
            if -line_height < y < video_height:
                # 计算文字宽度，使文字居中
                text_width = draw.textlength(line, font=font)
                x = (video_width - text_width) // 2
                
                # 绘制文字
                draw.text((x, y), line, font=font, fill=font_color)
        
        # 将PIL图像转换为numpy数组
        return np.array(img)
    
    # 创建视频剪辑
    video_clip = VideoClip(make_frame, duration=total_duration)
    
    # 设置视频参数
    video_clip = video_clip.with_fps(fps)
    
    # 输出视频文件
    video_clip.write_videofile(output_file, codec='libx264', audio=False)
    
    print(f"视频已生成：{output_file}")

if __name__ == "__main__":
    # 示例用法
    input_text_file = "test_text.txt"
    output_video_file = "scrolling_text_video.mp4"
    
    create_scrolling_text_video(input_text_file, output_video_file)
