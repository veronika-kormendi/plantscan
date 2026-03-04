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

start_corner = None
end_corner = None
drawn_rect = None
moving_rect = None
rect_id = None
offset_x = None
offset_y = None
mode = None # drawing/moving/none

# ---------- GUI ------------
gui_window = tk.Tk() # creating a window instance
gui_window.title("is_it_plant_based?") # add gui window title
gui_window.iconbitmap('C:\\Users\\veron\\Downloads\\isitpb.ico') # adding icon to gui window
style_obj = ttk.Style(theme="vapor") # applying theme
width = gui_window.winfo_screenwidth() # set window width
height = gui_window.winfo_screenheight() # set window height
gui_window.geometry(f"{width}x{height}+0+0") # window size with width, height, offset, offset
# ---------- CANVAS ------------
canvas = tk.Canvas(gui_window, width=width, height=height) # creating a canvas to display the image on
# open image file - JPG
def select_img_from():
    file_to_open = filedialog.askopenfilename(title="Select Image", filetypes=(("JPG files", "*.jpg"),))
    if not file_to_open: # if the file does not exist
        return None
    opened_pil_img = Image.open(file_to_open)
    return opened_pil_img

# resize image proportionately to fit to screen
def resize_image(image, new_w=600):
    img_w, img_h = image.size
    new_h = int(img_h * new_w / img_w)
    resized_image = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
    return resized_image

# turn image opened with PIL to tk compatible image
def make_tk_img(resized_image):
    tk_img = ImageTk.PhotoImage(resized_image)
    return tk_img

def display_image(tk_img):
    canvas.delete("all")
    rect_id = None
    start_corner = None
    end_corner = None
    mode = None
    canvas.create_image(10,10, anchor=tk.NW, image=tk_img) # adding tkinter image to canvas
    canvas.image = tk_img
    print("displaying image", tk_img) # for troubleshooting

def run_img_tasks():
    opened_img_pil = select_img_from()
    resized_image = resize_image(opened_img_pil)
    tk_img = make_tk_img(resized_image)
    display_image(tk_img)

# ----- BUTTON ---------
select_img_btn = tk.Button(gui_window, text="Select Image", padx=10, pady=2, command=run_img_tasks)
select_img_btn.pack()

def draw_rectangle():
    global rect_id
    if start_corner is None or end_corner is None:
        return
    x0, y0 = start_corner
    x1, y1 = end_corner
    if rect_id is None:
        rect_id = canvas.create_rectangle(x0, y0, x1, y1, outline="red", width=4)  # create rectangle
    else:
        canvas.coords(rect_id, x0, y0, x1, y1)

def get_rect_coords():
    if rect_id is None:
        return None
    coords = canvas.coords(rect_id)
    if len(coords) !=4:
        return None
    x0, y0, x1, y1 = coords
    x0, x1 = sorted((x0, x1))
    y0, y1 = sorted((y0, y1))
    return x0, y0, x1, y1

def is_click_in_rect(x, y):
    rect_coords = get_rect_coords()
    if rect_coords is None:
        return False
    x0, y0, x1, y1 = rect_coords
    return x0 <= x <= x1 and y0 <= y <= y1

def on_click(event):
    global start_corner, end_corner, rect_id, mode, offset_x, offset_y
    if rect_id is None: # scenario 1 - if rectangle does not exist
        mode = "drawing"
        # start drawing the rectangle
        start_corner = (event.x, event.y)  # drag point - drag starts here
        end_corner = (event.x, event.y)  # release point - drag ends here
        draw_rectangle() #display rectangle with start_corner dragged to end corner
        return
    # scenario 2 - rectangle exists,  so check if click is inside the rect
    if is_click_in_rect(event.x, event.y): # if click is inside the rect, drag it
        mode = "moving" # we want to move the existing rect
        x0, y0, x1, y1 = canvas.coords(rect_id)
        offset_x = event.x - x0
        offset_y = event.y - y0
        return
    # scenario 3 - when click is outside of rect - draw a new rectangle
    canvas.delete(rect_id)
    rect_id = None # reset
    mode = "drawing"
    start_corner = (event.x, event.y)
    end_corner = (event.x, event.y)
    draw_rectangle()

def drag_rect(event):
    global end_corner
    if mode == "drawing":
        end_corner = (event.x, event.y)
        draw_rectangle()
    elif mode == "moving":
        x0,y0,x1,y1= canvas.coords(rect_id)
        dx = event.x - (x0+offset_x)
        dy = event.y - (y0+offset_y)
        canvas.move(rect_id, dx, dy)

def on_release(event): # when mouse is released
    global mode
    mode = None

canvas.bind("<Button-1>", on_click)
canvas.bind("<B1-Motion>", drag_rect)
canvas.bind("<ButtonRelease-1>", on_release)
canvas.pack()
gui_window.mainloop() # displaying the window & listen for events