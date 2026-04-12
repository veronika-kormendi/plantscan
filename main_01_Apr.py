''' Author: Veronika Kormendi
    Purpose: Final Year Project
'''
# ------- IMPORTS -------
import os
from PIL import Image, ImageTk  # for managing images
import pillow_heif # for HEIC to JPG conversion
import tkinter as tk # for GUI
import cv2 as cv # openCV
import ttkbootstrap as ttk # for modern GUI
from tkinter import filedialog
from paddleocr import PaddleOCR
import json
import string
import unicodedata
import Levenshtein

start_corner = None
end_corner = None
drawn_rect = None
moving_rect = None
rect_id = None
offset_x = None
offset_y = None
mode = None # drawing/moving/none
resized_image = None
output_path = None # working path
rotation_angle = None
canvas_img_id = None

# ---------- GUI ------------
gui_window = tk.Tk() # creating a window instance
gui_window.title("is_it_plant_based?") # add gui window title
gui_window.iconbitmap('C:\\Users\\veron\\Downloads\\isitpb.ico') # adding icon to gui window
style_obj = ttk.Style(theme="vapor") # applying theme
width = gui_window.winfo_screenwidth() # set window width
height = gui_window.winfo_screenheight() # set window height
gui_window.geometry(f"{width}x{height}+0+0") # window size with width, height, offset, offset

# step 1 - img conversion: HEIC to JPG
input_folder = 'G:\\My Drive\\plantscan_photos_to_process'
output_folder = 'G:\\My Drive\\plantscan_photos_to_process\\jpg_folder'

# open & save HEIC to JPG img
def heic_to_jpg(input_path, output_path):
    pillow_heif.register_heif_opener() # to be able to open HEIC files
    if not os.path.exists(output_folder): # if output folder does not exist
        os.makedirs(output_folder) # create one
    filename = os.path.basename(input_path) # getting the filename
    jpg_filename = f"{os.path.splitext(filename)[0]}.jpg" # build jpg filename
    jpg_path = os.path.join(output_folder, jpg_filename) #build jpg path where to save the jpg img
    try:
        img = Image.open(input_path)  # open img from input path
        img.save(jpg_path, format='JPEG') # save jpg
    except Exception as e: # error handling
        print(f"Heic conversion error occurred: {e}")
        return
    print(f"File extension changed from {filename} to JPG")

# ------- GREYSCALE ----------
greyscale_output_folder = 'G:\\My Drive\\plantscan_photos_to_process\\new_test'
def colour_to_greyscale(coloured_img):
    # path = join input folder & selected coloured image
    img_to_greyscale = os.path.join(output_folder, coloured_img)
    if not os.path.exists(greyscale_output_folder):
        os.makedirs(greyscale_output_folder)
    gscale_output = os.path.join(greyscale_output_folder, coloured_img)
    gscale_filename = os.path.basename(gscale_output)
    coloured_img = cv.imread(img_to_greyscale)
    greyscale_img = cv.cvtColor(coloured_img, cv.COLOR_BGR2GRAY) #convert to gscale
    cv.imwrite(gscale_output, greyscale_img) # saving the greyscale image to the output folder
    print(f"Greyscale conversion successful: {gscale_filename} is greyscale now.")


#continue

# ---------- CANVAS ------------
canvas = tk.Canvas(gui_window, width=width, height=height) # creating a canvas to display the image on
canvas.bind("<Button-1>", on_click)
canvas.bind("<B1-Motion>", drag_rect)
canvas.bind("<ButtonRelease-1>", on_release)
# save_btn = tk.Button(gui_window, text="Save Crop", command=save_cropped_img)
save_btn = tk.Button(gui_window, text="Save Crop", command=save_crop_and_start_ocr)
save_btn.pack()
canvas.pack()
gui_window.mainloop() # displaying the window & listen for events