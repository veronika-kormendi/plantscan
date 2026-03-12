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
import math
import time

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

# step 1 - img conversion: HEIC to JPG

input_folder = 'G:\\My Drive\\plantscan_photos_to_process'
output_folder = 'G:\\My Drive\\plantscan_photos_to_process\\to_jpg'

# open & save HEIC to JPG img
def heic_to_jpg(input_path):
    pillow_heif.register_heif_opener() # to be able to open HEIC files
    if not os.path.exists(output_folder): # if output folder does not exist
        os.makedirs(output_folder) # create one
    filename = os.path.basename(input_path)
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

# open image file - JPG
def select_img_from():
    file_to_open = filedialog.askopenfilename(title="Select Image", filetypes=(("Supported image files", "*.jpg *.heic *.HEIC *.jpeg"),))
    if not file_to_open: # if the file does not exist
        return None
    # opened_pil_img = Image.open(file_to_open)
    # return opened_pil_img # returns PIL image
    return file_to_open # return filepath

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
    global rect_id, start_corner,end_corner, mode
    canvas.delete("all")
    rect_id = None
    start_corner = None
    end_corner = None
    mode = None
    canvas.create_image(10,10, anchor=tk.NW, image=tk_img) # adding tkinter image to canvas
    canvas.image = tk_img
    print("displaying image", tk_img) # for troubleshooting

def run_img_tasks():
    global resized_image, output_path
    selected_path = select_img_from() # open img file
    if not selected_path:
        return
    filename = os.path.basename(selected_path)
    extension = filename. lower().split('.')[-1]
    if extension == "heic":
        heic_to_jpg(selected_path) # convert heic to jpg
        filename = filename.replace('.heic', '.jpg').replace('HEIC', 'jpg') # replace extension
        output_path = os.path.join(output_folder, filename) #add converted file to
    else:
        output_path = os.path.join(output_folder, filename)
        if not os.path.exists(output_path):
            os.makedirs(output_folder, exist_ok=True)
    colour_to_greyscale(os.path.basename(output_path)) # turn into greyscale
    gscale_path = os.path.join(greyscale_output_folder, os.path.basename(output_path))
    pil_img = Image.open(gscale_path) # load image
    resized_image = resize_image(pil_img)  #resize image
    tk_img = make_tk_img(resized_image) # convert to tk img
    display_image(tk_img) # display


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
        rect_id = canvas.create_rectangle(x0, y0, x1, y1, outline="red", width=2)  # create rectangle
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
    # time.sleep(30)
    # rotate_rect(rect_id, 10) # test rotation with a value
    # this produced a shifted rectangle, not rotated, it is axis aligned unfortunately
    make_poly()
def shift_coords(x0,y0,x1,y1):
    return x0-12,y0-12, x1-12, y1-12

def make_poly():
    rect_coords = get_rect_coords()
    if rect_coords is None:
        print("no rect coords")
        return
    x0, y0, x1, y1 = rect_coords
    # points = [x0,y0,x1,y0,x1,y1,x0,y1]
    # poly = canvas.create_polygon(points, outline="blue", width=2)

    # center_x = (x0+y0)/2
    # center_y = (y0+y1)/2
    center_x = (x0+x1)/2
    center_y = (y0+y1)/2

    half_width = abs(x1-x0)/2 # x middle
    half_height = abs(y1-y0)/2 # y middle

    #double the width of half_width to get full width of rectangle
    top_right_x = half_width * 2 # xtr
    # double the height of half height to get full height of rect
    bott_left_x = half_height*2 #xbr
    top_right = (top_right_x)
    bott_left = (bott_left_x)
    new_center = x0, y0 # this is top left corner
    bott_right = x1, y1
    print(new_center, top_right, bott_left, bott_right)
    poly = canvas.create_polygon(new_center, top_right, bott_left, bott_right, fill="red") # displays a triangle instead of a rectangle
   # print("center coords:", center_x, center_y)
    #print(tl, tr, bl, br)
    #new_points = [tl, tr, bl, br]
    # these are the points of 1/4 of the rectangle
    #
    #print("new_points:", new_points)
    #poly = canvas.create_polygon(, outline="red", fill="red") #displays 1/4 filled rectangle
    # print(center_x, center_y)
    # tr = -center_x
    # bl = -center_y
    # print(tr, bl)
    # poly = canvas.create_polygon(center_x, center_y, tr, bl, outline="red", fill="red")




# def rotate_rect(rect_id, rotate_angle):
#     rect_coords = get_rect_coords() # getting the rect coords
#     print("coords before rotation:", rect_coords) # displaying them for debug
#     if rect_coords is None:
#         print("no rect coords") # error message
#         return
#     x0, y0, x1, y1 = rect_coords # coords
#     # we rotate from x_center & y_center
#     x_center = (x0 + x1) / 2 # middle of x start & end points
#     y_center = (y0 + y1) / 2 # middle of y start and end
#     angle = math.radians(rotate_angle) # convert rotate degree to radian
#     #rotate point by the centre
#     def rotate_coords(x,y):
#         dx = x - x_center # offset/point from center
#         dy = y - y_center
#         cos_angle = math.cos(angle)
#         sin_angle = math.sin(angle)
#         xrot = x_center + dx * cos_angle - dy * sin_angle # calculate rotation
#         yrot = y_center + dx * sin_angle + dy * cos_angle
#         return xrot, yrot #return rotated points
#     new_x0, new_y0 = rotate_coords(x0, y0) # rotate start
#     new_x1, new_y1 = rotate_coords(x1, y1) # rotate end
#     canvas.coords(rect_id, new_x0, new_y0, new_x1, new_y1)
#
#     print("rotate ran") # print for debug purposes
#




def save_cropped_img():
    cropped_folder = 'G:\\My Drive\\plantscan_photos_to_process\\cropped_images'
    global resized_image, output_path
    if resized_image is None:
        print("No image loaded.")
        return
    if output_path is None:
        print("No output path was provided.")
        return
    rect = get_rect_coords()
    if rect is None:
        print("No rectangle drawn.")
        return
    # canvas coords to image coords since
    # rectangle is in canvas coords & cropped img is in other coords
    x0, y0, x1, y1 = shift_coords(*canvas.coords(rect_id))
    cropped = resized_image.crop((x0, y0, x1, y1))
    if not os.path.exists(cropped_folder): #if it does not exist
        os.makedirs(cropped_folder) # create cropped folder
    original_name = os.path.basename(output_path) #original name
    base, _ = os.path.splitext(original_name)
    new_name = f"{base}_cropped.jpg"
    # save_path = filedialog.asksaveasfilename(defaultextension=".png")
    save_path = os.path.join(cropped_folder, new_name) # where to save the new one
    if save_path:
        cropped.save(save_path, format="JPEG")
        print(f"Saved cropped image to {save_path}.")


canvas.bind("<Button-1>", on_click)
canvas.bind("<B1-Motion>", drag_rect)
canvas.bind("<ButtonRelease-1>", on_release)
save_btn = tk.Button(gui_window, text="Save Crop", command=save_cropped_img)
save_btn.pack()
canvas.pack()
gui_window.mainloop() # displaying the window & listen for events