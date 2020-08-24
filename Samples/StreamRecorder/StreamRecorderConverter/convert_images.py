"""
 Copyright (c) Microsoft. All rights reserved.
 This code is licensed under the MIT License (MIT).
 THIS CODE IS PROVIDED *AS IS* WITHOUT WARRANTY OF
 ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING ANY
 IMPLIED WARRANTIES OF FITNESS FOR A PARTICULAR
 PURPOSE, MERCHANTABILITY, OR NON-INFRINGEMENT.
"""
import os
from cv2 import cv2 # to make sure vscode recognize modules
import argparse
import numpy as np
import multiprocessing
from pathlib import Path

from utils import folders_extensions


def write_to_png(path, is_ahat):
    print(".", end="", flush=True)
    # print('Processing ', path)

    output_path = path.replace('pgm', 'png')
    if os.path.exists(output_path):
        pass

    img = cv2.imread(path, -1)
    v_min = img.min()
    v_max = img.max()
    img = (img - v_min) / (v_max - v_min)

    cv2.imwrite(output_path, (img * 255).astype(np.uint8))


def write_bytes_to_png(bytes_path, width, height):
    print(".", end="", flush=True)

    output_path = bytes_path.replace('bytes', 'png')
    if os.path.exists(output_path):
        return

    image = []
    with open(bytes_path, 'rb') as f:
        image = np.frombuffer(f.read(), dtype=np.uint8)

    image = image.reshape((height, width, 4))

    new_image = image[:, :, :3]
    cv2.imwrite(output_path, new_image)

    # Delete '*.bytes' files
    bytes_path.unlink()



def get_width_and_height(path):
    with open(path) as f:
        lines = f.readlines()
    (_, _, width, height) = lines[0].split(',')

    return (int(width), int(height))


def convert_images(folder):
    p = multiprocessing.Pool(multiprocessing.cpu_count())
    for (img_folder, extension) in folders_extensions:
        if img_folder == 'rgb':
            pv_path = list(folder.glob('*pv.txt'))
            assert len(list(pv_path)) == 1 
            (width, height) = get_width_and_height(pv_path[0])

            paths = (folder / img_folder).glob('*bytes')
            print("Processing images")
            for path in paths:
                p.apply_async(write_bytes_to_png, (str(path), width, height))
        elif img_folder == 'ahat' or img_folder == 'lt':
            paths = (folder / img_folder).glob(f'{extension}')
            is_ahat = (img_folder == 'ahat')
            for path in paths:
                p.apply_async(write_to_png, (str(path), is_ahat))
    p.close()
    p.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert images')
    parser.add_argument("--recording_path", required=True,
                        help="Path to recording folder")
    args = parser.parse_args()
    convert_images(Path(args.recording_path))