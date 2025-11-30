import numpy as np
from PIL import Image
import os
import time
import sys
import platform

Ascii = list(
    " !\"%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
)


def LoadImg(i, j, picture, scale=6):
    img = Image.open(picture)
    weight, height = img.size
    img = img.resize((int(weight / scale), int(height / scale)))
    img = np.array(img)
    # print(img.shape)
    img[:, :, i] = img[:, :, i] * 0
    img[:, :, j] = img[:, :, j] * 0
    convert_img = img[:, :, 0] + img[:, :, 1] + img[:, :, 2]
    return convert_img


def genPics(progress_callback=None, scale=6):
    vName = "output"
    picDirPath = "./imgout/"
    charDirPath = "./textout/"
    if not os.path.exists(charDirPath):
        os.makedirs(charDirPath)

    pics = [p for p in os.listdir(picDirPath) if p.endswith((".jpg", ".png", ".jpeg"))]
    try:
        pics.sort(key=lambda x: int(x[6:-4]))
    except:
        pass

    total_pics = len(pics)
    index = 0
    for i, pic in enumerate(pics):
        if progress_callback:
            progress_callback(i, total_pics)

        img = LoadImg(0, 2, os.path.join(picDirPath, pic), scale=scale)
        with open(os.path.join(charDirPath, vName + str(index) + ".txt"), "w") as f:
            for m in range(img.shape[0]):
                for n in range(img.shape[1]):
                    code = img[m][n]
                    f.write(Ascii[int(code / 100)])
                    f.write(Ascii[int(code / 100)])
                f.write("\n")
        index = index + 1


def show(delay=0.02, skip=0):
    charDirPath = "./textout/"
    if not os.path.exists(charDirPath):
        print("No text output found.")
        return

    txts = [t for t in os.listdir(charDirPath) if t.endswith(".txt")]
    try:
        txts.sort(key=lambda x: int(x[6:-4]))
    except ValueError:
        pass

    for i, txt in enumerate(txts):
        if skip > 0 and i % (skip + 1) != 0:
            continue
        full_path = os.path.normpath(os.path.join(charDirPath, txt))
        if platform.system() == "Windows":
            os.system(f'type "{full_path}"')
        else:
            os.system(f'cat "{full_path}"')
        time.sleep(delay)


if __name__ == "__main__":
    delay = 0.02
    skip = 0
    if len(sys.argv) > 1:
        try:
            delay = float(sys.argv[1])
        except ValueError:
            pass
    if len(sys.argv) > 2:
        try:
            skip = int(sys.argv[2])
        except ValueError:
            pass
    show(delay, skip)
