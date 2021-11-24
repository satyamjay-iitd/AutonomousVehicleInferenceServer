import cv2
import glob
import re

img_array = []


numbers = re.compile('(\d+)')

def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts


def img_2_video(outfile_path, fps):
    for filename in sorted(glob.glob('temp/imgs/new/*.png'), key=numericalSort):
        img = cv2.imread(filename)
        height, width, layers = img.shape
        size = (width, height)
        img_array.append(img)

    out = cv2.VideoWriter(outfile_path, cv2.VideoWriter_fourcc(*'DIVX'), fps, size)

    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()