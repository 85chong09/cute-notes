#!/usr/bin/env python3
"""
自动生成可爱便签应用图标
"""
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("⚠️  未安装Pillow库")
    print("🔧 请运行: pip install Pillow")
    sys.exit(1)

def create_note_icon(size, bg_color, note_color, line_color):
    """创建一个简单的记事本图标"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制背景圆形
    margin = size // 16
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill=bg_color,
        outline=(200, 180, 160, 255),
        width=2
    )
    
    # 绘制记事本
    note_margin = size // 5
    note_size = size - note_margin * 2
    
    # 记事本背景
    draw.rectangle(
        [note_margin, note_margin, note_margin + note_size, note_margin + note_size],
        fill=note_color,
        outline=(180, 160, 140, 255),
        width=2
    )
    
    # 绘制线条
    line_count = 3
    line_start = note_margin + note_size // 3
    line_spacing = note_size // (line_count + 1)
    
    for i in range(line_count):
        y = line_start + i * line_spacing
        draw.line(
            [note_margin + 8, y, note_margin + note_size - 8, y],
            fill=line_color,
            width=1
        )
    
    return img

def main():
    # 图标输出目录
    icons_dir = os.path.join(os.path.dirname(__file__), 'src-tauri', 'icons')
    os.makedirs(icons_dir, exist_ok=True)
    
    # 颜色配置
    bg_color = (255, 200, 150, 255)      # 暖橙色背景
    note_color = (255, 248, 240, 255)    # 米色纸张
    line_color = (200, 180, 160, 200)     # 淡棕色线条
    
    # 需要创建的图标尺寸
    sizes = [32, 128]
    
    print("🎨 正在生成图标...")
    print("=" * 50)
    
    for size in sizes:
        img = create_note_icon(size, bg_color, note_color, line_color)
        output_path = os.path.join(icons_dir, f'{size}x{size}.png')
        img.save(output_path)
        print(f"✅ 已创建: {size}x{size}.png")
    
    print("=" * 50)
    print(f"📁 图标保存在: {icons_dir}")
    print("🚀 现在可以运行: cargo tauri dev")
    
    # Windows ICO格式（可选）
    try:
        # 创建多尺寸ICO文件
        icon_sizes = [16, 24, 32, 48, 64, 128, 256]
        icons = []
        
        for size in icon_sizes:
            img = create_note_icon(size, bg_color, note_color, line_color)
            icons.append(img)
        
        ico_path = os.path.join(icons_dir, 'icon.ico')
        icons[0].save(
            ico_path,
            format='ICO',
            sizes=[(s, s) for s in icon_sizes]
        )
        print(f"✅ 已创建: icon.ico (Windows)")
    except Exception as e:
        print(f"⚠️  创建ICO文件失败: {e}")
        print("   这不是必需的，可以继续开发")

if __name__ == "__main__":
    main()
