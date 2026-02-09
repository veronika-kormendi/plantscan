''' Author: Veronika Kormendi
    Purpose: Final Year Project
'''
import os
from PIL import Image
import pillow_heif
import cv2 as cv
import numpy as np

# step 1 - img conversion: HEIC to JPG

input_folder = 'G:\\My Drive\\plantscan_photos_to_process'
output_folder = 'G:\\My Drive\\plantscan_photos_to_process\\converted_to_jpg'

"""save HEIC to JPG path"""
def heic_to_jpg(heic_path, jpg_path):
    img = Image.open(heic_path)
    img.save(jpg_path, format='JPEG')

def convert_multiple_heic_to_jpg(input_folder, output_folder):
    # register HEIF opener with Pillow
    pillow_heif.register_heif_opener()
    # create output folder if it does not exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.heic'):
            heic_path = os.path.join(input_folder, filename)
            jpg_filename = f"{os.path.splitext(filename)[0]}.jpg"
            jpg_path = os.path.join(output_folder, jpg_filename)
            heic_to_jpg(heic_path, jpg_path)
            print(f"Converting {filename} to JPG")

# step 2 - colour to greyscale img

convert_multiple_heic_to_jpg(input_folder, output_folder)

greyscale_input_folder = 'G:\\My Drive\\plantscan_photos_to_process\\converted_to_jpg'
greyscale_output_folder = 'G:\\My Drive\\plantscan_photos_to_process\\greyscale'
def colour_to_greyscale(greyscale_input_folder, greyscale_output_folder):
    if not os.path.exists(greyscale_output_folder):
        os.makedirs(greyscale_output_folder)
    for file in os.listdir(greyscale_input_folder):
        colour_path = os.path.join(greyscale_input_folder, file)
        greyscale_path = os.path.join(greyscale_output_folder, file)
        img = cv.imread(colour_path) # read image
        greyscale_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY) # convert to greyscale
        cv.imwrite(greyscale_path, greyscale_img) # saving the greyscale img to the output folder
        print(f"converting {file} to greyscale")
colour_to_greyscale(greyscale_input_folder, greyscale_output_folder)