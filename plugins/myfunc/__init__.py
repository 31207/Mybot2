import string

from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command, on_message
from nonebot.adapters import Message
from nonebot.plugin.on import on_shell_command
from nonebot.rule import fullmatch, RegexRule
from nonebot.params import CommandArg, Arg
from nonebot.adapters.onebot.v11 import Event, PrivateMessageEvent, GroupMessageEvent
from nonebot_plugin_alconna.builtins.extensions.telegram import on_bot_connect

from . import utils
from .config import Config
from nonebot.log import logger
import random
import subprocess
from .otto import HZYS
from nonebot_plugin_alconna.uniseg import UniMessage

__plugin_meta__ = PluginMetadata(
    name='myfunc',
    description='',
    usage='',
    config=Config,
)

config = get_plugin_config(Config)

echo = on_message(priority=10, block=False)

command_i_love_you = on_command('我喜欢你', rule=fullmatch('我喜欢你'), priority=10, block=False)
# command_mute = on_command('禁言',priority=10, block=False)
command_mirror = on_command('镜像', rule=RegexRule('^镜像(?:[左右上下])?$'), priority=10, block=False)
command_hzys = on_command('活字印刷', priority=10, block=False, force_whitespace=' ')
command_worship = on_command('膜拜', priority=10, block=False)
command_point = on_command('指', priority=10, block=False, force_whitespace=' ')
command_bro = on_command('兄弟', priority=10, block=False, force_whitespace=' ')
command_shell = on_command('shell', priority=10, block=False, force_whitespace=' ')
command_count = on_command('count', priority=10, block=False, force_whitespace=' ')
command_exec = on_command('exec', priority=10, block=False, force_whitespace=' ')
command_captcha = on_command('验证码', priority=10, block=False, force_whitespace=' ')
command_config = on_command('config', priority=10, block=False, force_whitespace=' ')


@command_i_love_you.handle()
async def _(event: GroupMessageEvent):
    # await command_i_love_you.finish('你喜欢我')
    pass


@command_mirror.got('arg1', prompt='请发送方向(左/上/右/下)')
@command_mirror.got('arg2', prompt='请发送图片')
async def _(event: GroupMessageEvent, arg1: Message = Arg()):
    tmp = {
        '左': 0,
        '上': 1,
        '右': 2,
        '下': 3,
    }
    try:
        direction = tmp[str(arg1)]
    except:
        logger.error('非法方向')
        await UniMessage.at(event.get_user_id()).text('没有这个方向！').finish()
        return
    pic_urls = utils.get_pic_urls(event.model_dump())
    pic_urls_count = len(pic_urls)
    original_pic_path = f'{utils.plugin_path}/tmp/{event.user_id}.gif'
    mirrored_pic_path = f'{utils.plugin_path}/tmp/{event.user_id}_mirrored.gif'
    if pic_urls_count < 1:
        await UniMessage.at(event.get_user_id()).text('不是图片！').finish()
    if pic_urls_count > 1:
        await UniMessage.at(event.get_user_id()).text(
            f'图片数量为{pic_urls_count},只需要一张图片！请重新输入命令').finish()
    print(pic_urls)
    pic_url = pic_urls[0]
    await UniMessage.at(event.get_user_id()).text('正在镜像ing...').send()
    ret = await utils.download_pic(pic_url, original_pic_path)
    if ret == -1:
        await UniMessage.at(event.get_user_id()).text('图片下载失败').finish()
    utils.split_and_mirror_gif(original_pic_path, mirrored_pic_path, direction)
    await UniMessage.at(event.get_user_id()).image(raw=utils.get_bytes_from_file(mirrored_pic_path)).finish()


@command_hzys.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    if len(str(arg)) < 1:
        return
    if len(str(arg)) > 50:
        await UniMessage.at(event.get_user_id()).text('太长了！').finish()
    random_name = str(int(random.random() * 100000000))
    wav_name = 'wav_' + random_name
    wav_path = f'{utils.plugin_path}/otto/{wav_name}.wav'
    HZYS.export(str(arg), wav_name)
    await UniMessage.audio(raw=utils.get_bytes_from_file(wav_path)).finish()


@command_worship.handle()
async def _(event: GroupMessageEvent):
    qqids = utils.get_user_ids(event.model_dump())
    qqid_count = len(qqids)
    if qqid_count < 1:
        return
    if qqid_count > 1:
        await UniMessage.at(event.get_user_id()).text('at的人太多啦！').finish()
    qqid = qqids[0]
    path = f"{utils.plugin_path}/tkk/"
    random_name = str(int(random.random() * 100000000))
    avatar_name = 'avatar_' + random_name
    base_name = 'base_' + random_name
    mp4_name = 'mp4_' + random_name
    gif_name = 'gif_' + random_name
    commands = [
        f'curl "http://q.qlogo.cn/headimg_dl?dst_uin={qqid}&spec=640&img_type=jpg" --output {path}{avatar_name}.jpg',
        f'magick composite {path}{avatar_name}.jpg {path}mask.jpg -geometry 600x600+106+0 {path}{base_name}.jpg',
        f'ffmpeg -i {path}{base_name}.jpg -i {path}tkk.mp4 -filter_complex "[1:v]chromakey=0x00ff00:0.3:0.0[fg_keyed];[0:v][fg_keyed]overlay[out]" -map "[out]" -map 1:a -c:v libx264 -c:a aac -y {path}{mp4_name}.mp4',
        f'ffmpeg -i {path}{mp4_name}.mp4 -vf "scale=320:-1" -y {path}{gif_name}.gif',
        f'rm {path}{mp4_name}.mp4',
        f'rm {path}{base_name}.jpg',
        f'rm {path}{avatar_name}.jpg',
    ]
    # 使用 subprocess 运行命令
    for i in commands:
        result = subprocess.run(i, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("出错了")
            logger.error(result.stdout)
            logger.error(result.stderr)
            await UniMessage.at(event.get_user_id()).text('膜拜失败').finish()
    await UniMessage.at(event.get_user_id()).image(raw=utils.get_bytes_from_file(f'{path}{gif_name}.gif')).finish()


@command_point.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    if len(str(arg)) < 1:
        return
    if len(str(arg)) >= 10:
        logger.warning('指命令过长')
        await UniMessage.at(event.get_user_id()).text('太长啦！').finish()
    random_name = str(int(random.random() * 100000000))
    jpg_name = 'jpg_' + random_name
    path = f"{utils.plugin_path}/point/"
    commands = [
        f'magick convert {path}base.jpg -font {utils.plugin_path}/msyh.ttc -fill black -pointsize 24 -gravity center -annotate +0+80 "{str(arg)}" {path}{jpg_name}.jpg',
    ]
    # 使用 subprocess 运行命令
    for i in commands:
        result = subprocess.run(i, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("出错了")
            logger.error(result.stdout)
            logger.error(result.stderr)
            await UniMessage.at(event.get_user_id()).text('指人失败').finish()
            return
    await UniMessage.at(event.get_user_id()).image(raw=utils.get_bytes_from_file(f'{path}{jpg_name}.jpg')).finish()


@command_bro.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    if len(str(arg)) < 1:
        return
    if len(str(arg)) >= 10:
        logger.warning('兄弟命令过长')
        await UniMessage.at(event.get_user_id()).text('太长啦！').finish()
    random_name = str(int(random.random() * 100000000))
    jpg_name = 'jpg_' + random_name
    path = f"{utils.plugin_path}/bro/"
    commands = [
        f'magick convert {path}base.jpg -font {utils.plugin_path}/msyh.ttc -fill black -pointsize 30 -gravity center -annotate +0-100 "{str(arg)}" {path}{jpg_name}.jpg',
    ]
    # 使用 subprocess 运行命令
    for i in commands:
        result = subprocess.run(i, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("出错了")
            logger.error(result.stdout)
            logger.error(result.stderr)
            await UniMessage.at(event.get_user_id()).text('指人失败').finish()
    await UniMessage.at(event.get_user_id()).image(raw=utils.get_bytes_from_file(f'{path}{jpg_name}.jpg')).finish()


@command_shell.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    if event.group_id != 711674260:
        return
    result = subprocess.run(str(arg), shell=True, capture_output=True, text=True)
    await UniMessage.text(f'Stdout:\n{result.stdout}').text(f'Stderr:\n{result.stderr}').text(
        f'ReturnCode:{result.returncode}').finish()


@command_count.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    try:
        random_name = str(int(random.random() * 100000000))
        pic_name = 'count_' + random_name + '.gif'
        path = f"{utils.plugin_path}/moe-counter/{pic_name}"
        print(str(arg))
        utils.generate_count_pic(int(str(arg)), pic_name)
        await UniMessage.at(event.get_user_id()).image(raw=utils.get_bytes_from_file(path)).finish()
    except ValueError as e:
        logger.error(e)
        await UniMessage.at(event.get_user_id()).text(e).finish()


@command_exec.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    if event.group_id != 711674260:
        return
    exec(str(arg))
    await UniMessage.text('执行完毕').finish()


@command_captcha.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    text = str(arg)
    if len(text) <= 0:
        return
    if len(text) > 6:
        await UniMessage.at(event.get_user_id()).text('验证码太长了！').finish()
    legal_chars = string.digits + string.ascii_lowercase + string.ascii_uppercase
    for i in text:
        if i not in legal_chars:
            await UniMessage.at(event.get_user_id()).text('仅允许大小写字母和数字').finish()
    buf, _ = utils.generate_captcha_image(text=text)
    await UniMessage.at(event.get_user_id()).image(raw=buf).finish()


'''
    管理员控制config的更改
'''


@command_config.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    print(event.get_user_id(),arg)
    if event.get_user_id() != '3579148268':
        return
    if arg == 'test':
        await UniMessage.image(raw=utils.get_bytes_from_file(f'{utils.plugin_path}/tmp/BG.jpg')).finish()
    if arg == 'output_model_dump':
        config.output_model_dump = not config.output_model_dump
        if config.output_model_dump:
            await UniMessage.text('output_model_dump opening').finish()
        else:
            await UniMessage.text('output_model_dump closing').finish()
    if arg == 'output_pic_and_at_count':
        config.output_pic_and_at_count = not config.output_pic_and_at_count
        if config.output_pic_and_at_count:
            await UniMessage.text('output_pic_and_at_count opening').finish()
        else:
            await UniMessage.text('output_pic_and_at_count closing').finish()


@echo.handle()
async def _(event: Event):
    if config.output_model_dump:
        logger.debug(event.model_dump())
    if config.output_pic_and_at_count:
        logger.info(f'pic:{utils.get_pic_urls(event.model_dump(), True)},at:{utils.get_user_ids(event.model_dump())}')
