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


# step 1 - img conversion: HEIC to JPG

input_folder = 'G:\\My Drive\\plantscan_photos_to_process'
output_folder = 'G:\\My Drive\\plantscan_photos_to_process\\converted_to_jpg'

# convert all images at once
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

convert_multiple_heic_to_jpg(input_folder, output_folder)

# step 2 - colour to greyscale img
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

# ---------- GUI ------------
gui_window = tk.Tk() # creating a window instance
gui_window.title("is_it_plant_based?") # add gui window title
gui_window.iconbitmap('C:\\Users\\veron\\Downloads\\isitpb.ico') # adding icon to gui window
style_obj = ttk.Style(theme="vapor") # applying theme
width = gui_window.winfo_screenwidth() # set window width
height = gui_window.winfo_screenheight() # set window height
gui_window.geometry(f"{width}x{height}+0+0") # window size with width, height, offset, offset

# resize image proportionately to fit to screen
def resize_image(image):
    img_w, img_h = image.size
    new_w = 600
    new_h = int(img_h * new_w / img_w)
    resized_image = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
    return resized_image

img = Image.open(output_folder + "\\IMG_7760.jpg") # load an image to test how to display images
img_w, img_h = img.size # image size is set to img width and height
img = resize_image(img) # resizing the image
img_tk = ImageTk.PhotoImage(img) # convert to tkinter compatible format
gui_window.imgtk = img_tk


def cropClick():
    my_label = tk.Label(gui_window, text="Photo crop complete")
    my_label.pack()
my_button = tk.Button(gui_window, text="Crop", padx=10, pady=2, command=cropClick) # displays confirmation message when photo is cropped
my_button.pack() #display button
cropClick()


def display_image(image):
    canvas = tk.Canvas(gui_window, width=width, height=height) # creating a canvas to display the image on
    canvas.create_image(10,10, anchor=tk.NW, image=img_tk) # adding tkinter image to canvas
    canvas.pack() # display canvas with its contents

display_image(img_tk)

# def doSomething(event):
#     print("Doing something")
# gui_window.bind("<Button-3>", doSomething)

# # display an image
# def select_img():
#     global img_tk
#     filepath = filedialog.askopenfilename(title="Select Image", filetypes=(("image files", "*.jpg"),))
#     if filepath:
#         img = Image.open(filepath)
#         img.resize(size=(400, 400))
#         img_tk = ImageTk.PhotoImage(img) # load image
#
# img_label = tk.Label(gui_window, image=img_tk)
# img_label.pack()
# #         canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
# # canvas = tk.Canvas(gui_window, width=400, height=400)
# # canvas = tk.Canvas(gui_window, width=width, height=height)
#
# tk.Button(gui_window, text="Select Image", command=select_img).pack()

# canvas.pack()



gui_window.mainloop() # displaying the window & listen for events