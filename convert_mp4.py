# from moviepy.editor import *
import argparse
import cv2
import copy
from PIL import Image
import os
import shutil


parser = argparse.ArgumentParser(description="mp4转换gif")
parser.add_argument("load_path", type=str, help="视频读取路径")
parser.add_argument("save_path", type=str, help="视频保存路径")
parser.add_argument(
    "-S", "--size", type=float, default=0.5, help="视频缩放，格式为0-1之间的小数，默认为0.5"
)
parser.add_argument(
    "-K", "--keep", type=int, default=0, help="是否保留临时文件夹，1为是0为否，默认否"
)
parser.add_argument(
    "-R",
    "--reduce",
    type=int,
    default=1,
    help="抽帧，输入值代表隔几帧保存一次，默认1也即不抽帧",
)
args = parser.parse_args()

# def convert(load, save):
#     load_path = os.path.join(os.path.dirname(__file__), load)
#     save_path = os.path.join(os.path.dirname(__file__), save)
#     clip = (VideoFileClip(load_path))
#     clip.write_gif(save_path, fps=10)

# convert(args.load_path, args.save_path)

gif_frames = []


def convert_mp4_to_jpgs(input_file, temp):
    global gif_frames
    # 先将mp4文件的所有帧读取出保存为图片
    video_capture = cv2.VideoCapture(input_file)
    still_reading, image = video_capture.read()
    frame_count = 0
    while still_reading:
        # cv2.imwrite(os.path.join(temp, f"frame_{str(frame_count).zfill(3)}.jpg"), image)
        gif_frames.append(Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)))
        # read next image
        still_reading, image = video_capture.read()
        frame_count += 1


def convert_images_to_gif(output_file, temp):
    # 读取目录下图片，用Pillow模块的Image和所有图片合并成一张gif
    global gif_frames
    images = os.listdir(temp)
    images.sort()
    frames_origin = copy.deepcopy(gif_frames)
    frames = [
        frame.resize(
            (round(frame.width * args.size), round(frame.height * args.size)),
            Image.LANCZOS,
        )
        for frame in frames_origin
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
        append_images=[f for i, f in enumerate(frames[1:]) if i % args.reduce == 0],
        save_all=True,
        loop=0,
        duration=40,
    )

    gif_frames = []


def convert_mp4_to_gif(load, save):
    if not 0 < args.size <= 1:
        print("尺寸输入错误，应为0-1之间的小数")
        return
    load_path = os.path.join(os.path.dirname(__file__), load)
    save_path = os.path.join(os.path.dirname(__file__), save)
    tempdir = os.path.join(os.path.dirname(__file__), os.path.dirname(load), "output")
    if not os.path.exists(tempdir):
        os.mkdir(tempdir)
    convert_mp4_to_jpgs(load_path, tempdir)
    convert_images_to_gif(save_path, tempdir)
    if not args.keep:
        shutil.rmtree(tempdir)


convert_mp4_to_gif(args.load_path, args.save_path)
