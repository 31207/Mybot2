import io
import random
import string
import requests
from nonebot.log import logger
from PIL import Image, ImageSequence, ImageDraw, ImageFont, ImageFilter
import os
from pathlib import Path
plugin_path = os.path.dirname(os.path.abspath(__file__))

"""
    向data传入event.model_dump()即可获取消息中图片url
    include_reply: 是否在回复的原消息中获取图片url
"""
def get_pic_urls(data: dict, include_reply: bool = False) -> tuple:
    res = []
    try:
        msg = data['original_message']
        for i in msg:
            if i['type'] == 'image':
                res.append(i['data']['url'])
        if data['reply'] is not None and include_reply:
            msg = data['reply']['message']
            for i in msg:
                if i['type'] == 'image':
                    res.append(i['data']['url'])
        return tuple(res)

    except:
        logger.warning('取消息中图片url失败')
        return ()

def get_user_ids(data: dict) -> tuple:
    res = []
    try:
        msg = data['original_message']
        for i in msg:
            if i['type'] == 'at':
                res.append(i['data']['qq'])
        return tuple(res)
    except:
        logger.warning('取消息中被at者的qq号失败')
        return ()
async def download_pic(url:str,path:str):
    try:
        res = requests.get(url)
        if res.status_code==200:
            with open(path,'wb') as file:
                file.write(res.content)
        else:
            logger.error('download failed')
            logger.error(res)
            return -1
    except requests.exceptions.RequestException as e:
        logger.error(e)
        return -1
    return 0

def get_bytes_from_file(path: str):
    with open(path, 'rb') as file:
        return file.read()

def split_and_mirror_gif(gif_path, output_path, direction:int):
    # 读取原始GIF文件
    original_gif = Image.open(gif_path)
    frames = []
    durations = []
    width, height = original_gif.size
    middle_width = width // 2
    middle_height = height // 2
    # 遍历GIF的每一帧并进行镜像处理
    count = 0
    for frame in ImageSequence.Iterator(original_gif):
        new_frame = Image.new('RGBA', (width, height))
        # empty_frame = Image.new('RGBA', (width,height))
        if direction == 0:
            left_half = frame.crop((0, 0, middle_width, height))
            mirrored_half = left_half.transpose(Image.FLIP_LEFT_RIGHT)
            new_frame.paste(left_half, (0, 0))
            new_frame.paste(mirrored_half, (middle_width, 0))
        elif direction == 1:
            top_half = frame.crop((0, 0, width, middle_height))
            mirrored_half = top_half.transpose(Image.FLIP_TOP_BOTTOM)
            new_frame.paste(top_half, (0, 0))
            new_frame.paste(mirrored_half, (0, middle_height))
        elif direction == 2:
            right_half = frame.crop((middle_width, 0,width , height))
            mirrored_half = right_half.transpose(Image.FLIP_LEFT_RIGHT)
            new_frame.paste(mirrored_half, (0, 0))
            new_frame.paste(right_half, (middle_width, 0))
        elif direction == 3:
            top_half = frame.crop((0, middle_height, width, height))
            mirrored_half = top_half.transpose(Image.FLIP_TOP_BOTTOM)
            new_frame.paste(mirrored_half, (0, 0))
            new_frame.paste(top_half, (0, middle_height))

        frames.append(new_frame)
        if 'duration' in frame.info:
            durations.append(frame.info['duration'])
        count+=1

    if count!=1: frames[0].save(output_path, save_all=True, append_images=frames[1:], loop=0, duration=durations, disposal=2)
    else: frames[0].save(output_path, save_all=True, append_images=frames[1:], loop=0)

def generate_count_pic(count: int, output_file: str, theme: str = 'random'):
    folders = os.listdir(f'{plugin_path}/moe-counter/assets/theme/')
    if theme == 'random':
        theme = random.choice(folders)
    if theme not in folders:
        raise FileNotFoundError(f'未找到主题: {theme}')

    # 主题路径
    theme_dir = Path(f'{plugin_path}/moe-counter/assets/theme/{theme}')

    # 数字序列，例如显示 12345
    count_str = str(count)
    # 可选 _start/_end 图片
    use_start_end = True

    # 缩放比例
    scale = 1

    # 对齐方式: 'top', 'center', 'bottom'
    align = 'top'

    # 加载图片函数
    def load_char_image(char):
        img_file = Path(theme_dir / f"{char}.png")
        if not img_file.exists():
            img_file = Path(theme_dir / f"{char}.gif")
        if not img_file.exists():
            raise FileNotFoundError(f"没有找到字符图片: {char}")

        im = Image.open(img_file)
        if scale != 1:
            w, h = im.size
            im = im.resize((int(w * scale), int(h * scale)), Image.NEAREST)
        return im

    # 准备字符序列
    chars = list(count_str)
    if use_start_end:
        if (theme_dir / Path("_start.png")).exists() or (theme_dir / Path("_start.gif")).exists():
            chars.insert(0, "_start")
        if (theme_dir / Path("_end.png")).exists() or (theme_dir / Path("_end.gif")).exists():
            chars.append("_end")

    # 加载所有图片
    images = [load_char_image(c) for c in chars]

    # 计算最终 GIF 尺寸
    width = sum(im.width for im in images)
    height = max(im.height for im in images)

    # 创建空白画布
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    # 拼接图片
    x_offset = 0
    for im in images:
        y_offset = 0
        if align == 'center':
            y_offset = (height - im.height) // 2
        elif align == 'bottom':
            y_offset = height - im.height
        canvas.paste(im, (x_offset, y_offset), im if im.mode == 'RGBA' else None)
        x_offset += im.width

    # 保存为 GIF
    canvas.save(f'{plugin_path}/moe-counter/{output_file}', save_all=True, loop=0, duration=100)

def random_text(length=5, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(length))

def generate_captcha_image(text=None, width=160, height=60, fontsz=36):
    if text is None:
        text = random_text(5)
    # 生成背景
    img = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # 随机背景色块（轻微变化）
    for i in range(50):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = x1 + random.randint(1, 10)
        y2 = y1 + random.randint(1, 10)
        draw.rectangle([x1, y1, x2, y2], fill=(random.randint(200,255), random.randint(200,255), random.randint(200,255)))

    # 干扰线
    for i in range(6):
        start = (random.randint(0, width), random.randint(0, height))
        end = (random.randint(0, width), random.randint(0, height))
        draw.line([start, end], fill=(random.randint(50,160), random.randint(50,160), random.randint(50,160)), width=1)

    # 文字：逐字符绘制，带微小角度与位置偏移
    try:
        font = ImageFont.truetype(f'{plugin_path}/msyh.ttc', fontsz)
    except Exception:
        font = ImageFont.load_default()
    char_width = width // len(text)
    for i, ch in enumerate(text):
        # 单个字符画到单独图片上以便旋转
        char_img = Image.new('RGBA', (char_width, height), (255,255,255,0))
        cd = ImageDraw.Draw(char_img)
        # 随机颜色（深色）
        color = (random.randint(10,120), random.randint(10,120), random.randint(10,120))
        cd.text((5, random.randint(0, 8)), ch, font=font, fill=color)
        # 旋转
        angle = random.uniform(-30, 30)
        char_img = char_img.rotate(angle, resample=Image.BICUBIC, expand=1)
        # 粘贴回主图（随机Y偏移）
        px = i * char_width + random.randint(0, max(0, char_width - fontsz))
        py = random.randint(-5, 10)
        img.paste(char_img, (px, py), char_img)

    # 加噪点
    for _ in range(300):
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        img.putpixel((x, y), (random.randint(0,255), random.randint(0,255), random.randint(0,255)))

    # 轻微模糊/滤镜处理，让 OCR 更难
    img = img.filter(ImageFilter.SMOOTH)
    img = img.filter(ImageFilter.GaussianBlur(0.5))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf, text