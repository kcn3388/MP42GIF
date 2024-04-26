```
usage: convert_mp4.py [-h] [-S SIZE] [-K KEEP] [-R REDUCE] load_path save_path

mp4转换gif

positional arguments:
  load_path             视频读取路径
  save_path             视频保存路径

options:
  -h, --help            show this help message and exit
  -S SIZE, --size SIZE  视频缩放，格式为0-1之间的小数，默认为0.5
  -K KEEP, --keep KEEP  是否保留临时文件夹，1为是0为否，默认否
  -R REDUCE, --reduce REDUCE
                        抽帧，输入值代表隔几帧保存一次，默认1也即不抽帧
```