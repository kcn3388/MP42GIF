# from moviepy.editor import *
import argparse
import copy
import cv2
import os
import re
from typing import List

from PIL import Image

parser = argparse.ArgumentParser(description="mp4转换gif")
parser.add_argument("load_path", type=str, help="视频读取路径，可以是一个文件夹")
parser.add_argument(
    "save_path", type=str,
    help="视频保存路径，可以是一个文件夹。注意：读取的是文件夹时不支持指定保存的文件名"
)
# parser.add_argument("-F", "--folder", action='store_true', help="打开的是否文件夹，默认否")
parser.add_argument(
    "-S",
    "--size",
    type=float,
    default=0.5,
    help="视频缩放，格式为大于0的小数，默认为0.5"
)
parser.add_argument(
    "-R",
    "--reduce",
    type=int,
    default=1,
    help="抽帧，输入值代表隔几帧保存一次，默认1也即不抽帧",
)
parser.add_argument(
    "-D",
    "--duration",
    type=int,
    default=40,
    help="持续时间，默认40",
)
# parser.add_argument("-A", "--alpha", action='store_true', help="是否尝试转换为透明背景，默认否")
parser.add_argument(
    "-SP", "--split", action='store_true',
    help="是否保存拆分的GIF，默认否，不可与拼装GIF同时使用"
)
parser.add_argument(
    "-N", "--nogif", action='store_true',
    help="是否保存GIF，默认是，不可与拼装GIF同时使用"
)
parser.add_argument(
    "-C", "--combine", action='store_true',
    help="是否拼装一个GIF，默认否，不可与拆分、不保存GIF同时使用"
)
args = parser.parse_args()
gif_frames: List[Image.Image] = []


def convert_mp4_to_jpgs(input_file, split_path):
    global gif_frames
    # 先将mp4文件的所有帧读取出保存为图片
    video_capture = cv2.VideoCapture(input_file)
    still_reading, image = video_capture.read()
    frame_count = 0
    f_name = os.path.splitext(os.path.split(input_file)[-1])[0]
    os.makedirs(f"{split_path}/{f_name}") if not os.path.exists(f"{split_path}/{f_name}") else 0
    while still_reading:
        img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGBA))
        gif_frames.append(img)
        if args.split:
            img.save(f"{split_path}/{f_name}/{frame_count}.png", "PNG")
        # read next image
        still_reading, image = video_capture.read()
        frame_count += 1


def convert_images_to_gif(output_file):
    # 读取目录下图片，用Pillow模块的Image和所有图片合并成一张gif
    global gif_frames
    frames_origin: List[Image.Image] = copy.deepcopy(gif_frames)
    frames = [
        frame.resize(
            (round(frame.width * args.size), round(frame.height * args.size)),
            Image.LANCZOS,
        ) for frame in frames_origin
    ]
    # frames_rgba = []
    # for single_frame in frames:
    #     white_pixel = (255, 255, 255, 255)
    #     width, length = single_frame.size
    #     for h in range(width):
    #         for i in range(length):
    #             if single_frame.getpixel((h, i)) == white_pixel:
    #                 single_frame.putpixel((h, i), (0, 0, 0, 0))  # 设置透明
    #     frames_rgba.append(single_frame)
    #
    # final = frames_rgba if args.alpha else frames
    # frame_one = final[0]
    frame_one = frames[0]
    frame_one.save(
        f"{output_file}.gif",
        format="GIF",
        append_images=[
            # f for i, f in enumerate(final[1:]) if i % args.reduce == 0
            f for i, f in enumerate(frames[1:]) if i % args.reduce == 0
        ],
        save_all=True,
        loop=0,
        duration=args.duration,
    )

    gif_frames = []


def convert_mp4_to_gif(load, save):
    global gif_frames
    if args.combine and args.nogif:
        raise "参数冲突"
    if args.combine and args.split:
        raise "参数冲突"
    images = []
    if args.size <= 0:
        raise "尺寸输入错误，应为大于0的小数"
    load_path = os.path.join(os.getcwd(), load)
    if os.path.isdir(load_path):
        images = os.listdir(load)
        images.sort()
    elif os.path.isfile(load_path):
        images.append(load_path)
    else:
        raise "输入路径错误"
    for image in images:
        file_path = load_path
        if os.path.isdir(load_path):
            if args.combine:
                save_path = load_path
                pass
            else:
                file_path = os.path.join(os.getcwd(), load, image)
                image_file_name = os.path.splitext(os.path.split(image)[-1])
                if not re.match(r"\.mp4", image_file_name[-1], re.IGNORECASE):
                    continue
                save_path = os.path.join(os.getcwd(), save, image_file_name[0])
        else:
            save_path = os.path.join(os.getcwd(), save)
        if args.combine:
            for each in images:
                gif_frames.append(Image.open(f"{file_path}/{each}"))
            convert_images_to_gif(save_path)
            break
        else:
            convert_mp4_to_jpgs(file_path, save_path)
            convert_images_to_gif(save_path) if not args.nogif else 0


convert_mp4_to_gif(args.load_path, args.save_path)
