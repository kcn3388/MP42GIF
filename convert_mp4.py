# from moviepy.editor import *
import argparse
import cv2
import copy
from PIL import Image
import os

parser = argparse.ArgumentParser(description="mp4转换gif")
parser.add_argument("load_path", type=str, help="视频读取路径，当参数有F时，必须是一个文件夹")
parser.add_argument("save_path", type=str, help="视频保存路径，当参数有F时，必须是一个文件夹")
parser.add_argument("-F", "--folder", action='store_true', help="打开的是否文件夹，默认否")
parser.add_argument(
    "-S",
    "--size",
    type=float,
    default=0.5,
    help="视频缩放，格式为0-1之间的小数，默认为0.5"
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
args = parser.parse_args()
gif_frames = []


def convert_mp4_to_jpgs(input_file):
    global gif_frames
    # 先将mp4文件的所有帧读取出保存为图片
    video_capture = cv2.VideoCapture(input_file)
    still_reading, image = video_capture.read()
    frame_count = 0
    while still_reading:
        gif_frames.append(
            Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)))
        # read next image
        still_reading, image = video_capture.read()
        frame_count += 1


def convert_images_to_gif(output_file):
    # 读取目录下图片，用Pillow模块的Image和所有图片合并成一张gif
    global gif_frames
    frames_origin = copy.deepcopy(gif_frames)
    frames = [
        frame.resize(
            (round(frame.width * args.size), round(frame.height * args.size)),
            Image.LANCZOS,
        ) for frame in frames_origin
    ]
    frame_one = frames[0]
    # frame_one.save(
    #     output_file,
    #     format="GIF",
    #     append_images=frames[1:],
    #     save_all=True,
    #     loop=0,
    #     duration=25,
    # )
    frame_one.save(
        output_file,
        format="GIF",
        append_images=[
            f for i, f in enumerate(frames[1:]) if i % args.reduce == 0
        ],
        save_all=True,
        loop=0,
        duration=args.duration,
    )

    gif_frames = []


def convert_mp4_to_gif(load, save):
    images = []
    if not 0 < args.size <= 1:
        print("尺寸输入错误，应为0-1之间的小数")
        return
    if args.folder:
        images = os.listdir(load)
        images.sort()
    load_path = os.path.join(os.getcwd(), load)
    if not images:
        images.append(load_path)
    for image in images:
        if args.folder:
            load_path = os.path.join(os.getcwd(), load, image)
            image_file_name = os.path.splitext(os.path.split(image)[-1])[0]
            save_path = os.path.join(os.getcwd(), save, f"{image_file_name}.gif")
        else:
            save_path = os.path.join(os.getcwd(), save)
        convert_mp4_to_jpgs(load_path)
        convert_images_to_gif(save_path)


convert_mp4_to_gif(args.load_path, args.save_path)
