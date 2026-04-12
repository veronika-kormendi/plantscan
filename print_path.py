import os
from PIL import Image, ImageTk  # for managing images
import pillow_heif # for HEIC to JPG conversion
import tkinter as tk # for GUI
import cv2 as cv # openCV
import ttkbootstrap as ttk # for modern GUI
def colour_to_greyscale(input_folder, filename, output_folder):
    """Convert a colour image to greyscale and save it."""
    os.makedirs(output_folder, exist_ok=True)

    input_path = os.path.join(input_folder, filename)
    output_path = os.path.join(output_folder, filename)

    img = cv.imread(input_path)
    greyscale_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    cv.imwrite(output_path, greyscale_img)

    print(f"Greyscale conversion successful: {output_path}")
    return output_path
test_input_folder = 'G:\\My Drive\\plantscan_photos_to_process\\converted_to_jpg'
test_output_folder = 'G:\\My Drive\\plantscan_photos_to_process\\gscale_folder'
test_file = "IMG_7476.jpg"

# result = colour_to_greyscale(test_input_folder, test_file, test_output_folder)
# print(result)
# print(os.path.exists(result))

def display_path(input_folder, filename, output_folder):
    """display path of the input folder"""
    input_path = os.path.join(input_folder, test_file)
    output_path = os.path.join(output_folder, test_file)
    filename = os.path.basename(input_path)
    print(f"input path: {input_path}") # input path: G:\My Drive\plantscan_photos_to_process\converted_to_jpg\IMG_7476.jpg
    print(f"filename: {filename}") # filename: IMG_7476.jpg
    print(f"output_path: {output_path}") # output_path: G:\My Drive\plantscan_photos_to_process\gscale_folder\IMG_7476.jpg

display_path(test_input_folder, test_file, test_output_folder)
