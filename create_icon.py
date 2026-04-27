from PIL import Image, ImageDraw, ImageFont

def create_sticky_note_icon():
    size = 1024
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    margin = size // 16
    note_width = size - 2 * margin
    note_height = size - 2 * margin
    corner_size = size // 8
    
    # 便签主体 - 温暖的黄色
    note_color = (255, 235, 150, 255)  # 温暖的黄色
    shadow_color = (200, 180, 120, 100)   # 阴影色
    highlight_color = (255, 255, 200, 200)  # 高光色
    
    # 绘制阴影
    shadow_offset = size // 64
    draw.rounded_rectangle(
        [margin + shadow_offset, margin + shadow_offset, 
         margin + note_width + shadow_offset, margin + note_height + shadow_offset],
        radius=corner_size,
        fill=shadow_color
    )
    
    # 绘制便签主体
    draw.rounded_rectangle(
        [margin, margin, margin + note_width, margin + note_height],
        radius=corner_size,
        fill=note_color
    )
    
    # 绘制顶部高光
    highlight_height = size // 16
    draw.rounded_rectangle(
        [margin, margin, margin + note_width, margin + highlight_height + corner_size],
        radius=corner_size,
        fill=highlight_color
    )
    
    # 重新绘制顶部圆角区域的主体色，只保留高光
    draw.rectangle(
        [margin, margin + highlight_height, margin + note_width, margin + highlight_height + corner_size],
        fill=note_color
    )
    
    # 绘制便签顶部的胶带效果
    tape_width = size // 3
    tape_height = size // 20
    tape_x = (size - tape_width) // 2
    tape_y = margin - size // 40
    
    # 胶带（半透明的米白色）
    draw.rectangle(
        [tape_x, tape_y, tape_x + tape_width, tape_y + tape_height],
        fill=(245, 240, 230, 200)
    )
    
    # 胶带的阴影效果
    draw.line(
        [tape_x, tape_y + tape_height, tape_x + tape_width, tape_y + tape_height],
        fill=(200, 195, 185, 150),
        width=2
    )
    
    # 添加一个简单的铅笔图标在右下角
    pencil_size = size // 6
    pencil_x = size - margin - pencil_size - size // 16
    pencil_y = size - margin - pencil_size - size // 16
    
    # 铅笔身体
    draw.rectangle(
        [pencil_x, pencil_y + pencil_size // 4, 
         pencil_x + pencil_size, pencil_y + pencil_size * 3 // 4],
        fill=(255, 220, 150, 255)
    )
    
    # 铅笔尖
    draw.polygon(
        [(pencil_x, pencil_y + pencil_size // 4),
         (pencil_x - pencil_size // 4, pencil_y + pencil_size // 2),
         (pencil_x, pencil_y + pencil_size * 3 // 4)],
        fill=(180, 140, 100, 255)
    )
    
    # 铅笔尖的黑色部分
    draw.polygon(
        [(pencil_x - pencil_size // 8, pencil_y + pencil_size // 2 - pencil_size // 16),
         (pencil_x - pencil_size // 4, pencil_y + pencil_size // 2),
         (pencil_x - pencil_size // 8, pencil_y + pencil_size // 2 + pencil_size // 16)],
        fill=(50, 50, 50, 255)
    )
    
    # 橡皮擦
    draw.rectangle(
        [pencil_x + pencil_size * 3 // 4, pencil_y + pencil_size // 4,
         pencil_x + pencil_size, pencil_y + pencil_size * 3 // 4],
        fill=(255, 180, 180, 255)
    )
    
    # 添加一些简单的线条表示文字
    line_y_start = margin + size // 5
    line_spacing = size // 12
    left_margin = margin + size // 10
    right_margin = size - margin - size // 10
    
    for i in range(5):
        line_y = line_y_start + i * line_spacing
        # 随机长度的线条
        import random
        random.seed(i)  # 确保每次生成的图标都一样
        line_length = random.randint(
            (right_margin - left_margin) // 2,
            right_margin - left_margin
        )
        draw.line(
            [left_margin, line_y, left_margin + line_length, line_y],
            fill=(180, 160, 120, 200),
            width=size // 128
        )
    
    return img

if __name__ == '__main__':
    icon = create_sticky_note_icon()
    output_path = r'd:\tips\icon-source.png'
    icon.save(output_path, 'PNG')
    print(f'图标已保存到: {output_path}')
    print(f'图标尺寸: {icon.size}')
