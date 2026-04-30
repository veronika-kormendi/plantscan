import tkinter as tk # for GUI
import ttkbootstrap as ttk # for modern GUI
from config_refactor import *
# from postprocess_utils import postprocess_text
from postprocess_utils_return_filepath import postprocess_text
# from eval_utils_copy import evaluate_preprocessed
from eval_utils_copy_postp_return_filepath_not_folder import evaluate_preprocessed, evaluate_postprocessed
from tkinter import filedialog, messagebox
import pipeline
import os
from PIL import Image, ImageTk  # for managing images
import image_utils as img

start_corner = None # start corner of cropping rectangle
end_corner = None # end corner of cropping rectangle
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
gui_window.title(WINDOW_TITLE) # add gui window title
gui_window.iconbitmap(ICON_PATH) # adding icon to gui window
style_obj = ttk.Style(theme=THEME) # applying theme
width = gui_window.winfo_screenwidth() # set window width
height = gui_window.winfo_screenheight() # set window height
gui_window.geometry(f"{width}x{height}+0+0") # window size with width, height, offset, offset

def select_img_from():
    """Select an image from the input folder to start the pipeline.
    :returns: filepath of the image to be opened i.e. selected file"""
    file_to_open = filedialog.askopenfilename(title="Select Image", filetypes=SUPPORTED_IMAGE_TYPES)
    if not file_to_open:
        return None
    return file_to_open

def display_image(tk_img):
    """display image
    :param: tk_img: tk image"""
    global rect_id, start_corner, end_corner, mode, canvas_img_id
    canvas.delete("all")
    rect_id = None
    start_corner = None
    end_corner = None
    mode = None
    canvas_img_id = canvas.create_image(10, 10, anchor=tk.NW, image=tk_img)  # adding tkinter image to canvas
    canvas.image = tk_img
    print("displaying image", tk_img)  # for troubleshooting

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

def shift_coords(x0,y0,x1,y1):
    """shift the crop rectangle coordinates on the canvas from left top corner"""
    return x0-CROP_SHIFT,y0-CROP_SHIFT, x1-CROP_SHIFT, y1-CROP_SHIFT

def start_gui():
    gui_window.mainloop()  # displaying the window & listen for events

def run_img_tasks():
    global resized_image, output_path
    selected_path = select_img_from()
    if not selected_path:
        return
    gscale_img_path = pipeline.preprocess_image(selected_path)
    output_path = gscale_img_path
    pil_img = Image.open(gscale_img_path)
    resized_image = img.resize_image(pil_img)
    tk_img = img.make_tk_img(resized_image)
    display_image(tk_img)

def save_cropped_img():
    """save cropped image
    """
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
    if not os.path.exists(CROPPED_FOLDER): #if it does not exist
        os.makedirs(CROPPED_FOLDER) # create cropped folder
    original_name = os.path.basename(output_path) #original name
    base, _ = os.path.splitext(original_name)
    new_name = f"{base}_cropped.jpg"
    save_path = os.path.join(CROPPED_FOLDER, new_name) # where to save the new one
    if save_path:
        cropped.save(save_path, format="JPEG")
        print(f"Saved cropped image ({os.path.basename(save_path)}) to {save_path}.") # Saved cropped image (IMG_7476_cropped.jpg) to
    return save_path

def get_cropped_img(): # call pipeline
    """process cropped image"""
    cropped_img_path = save_cropped_img()
    if not cropped_img_path:
        return
    pipeline.process_cropped_image(cropped_img_path)

# ---------- CANVAS ------------
canvas = tk.Canvas(gui_window, width=width, height=height) # creating a canvas to display the image on
canvas.bind("<Button-1>", on_click)
canvas.bind("<B1-Motion>", drag_rect)
canvas.bind("<ButtonRelease-1>", on_release)
select_img_btn = tk.Button(gui_window, text="Select Image", padx=10, pady=2, command=run_img_tasks)
select_img_btn.pack(pady=6)
save_btn = tk.Button(gui_window, text="Save Crop", padx=10, pady=2, command=get_cropped_img)
save_btn.pack()

# eval_btn = tk.Button(gui_window, text="Evaluate Preprocessed", padx=10, pady=2,
#                      command=lambda: evaluate_preprocessed(ocr_extracted, CLEANED_FOLDER_PATH, "preprocessed_metrics.csv"))
# eval_btn.pack(pady=6)
#
# eval_btn = tk.Button(gui_window, text="postprocess", padx=10, pady=2,
#                      command=lambda: postprocess_text(CLEANED_FOLDER_PATH, POSTPROCESS_OUT_FOLDER))
# eval_btn.pack(pady=6)
#
#
# eval_btn = tk.Button(gui_window, text="Evaluate Postprocessed", padx=10, pady=2,
#                      command=lambda: evaluate_postprocessed(POSTPROCESS_OUT_FOLDER, "postprocessed_metrics.csv"))
# eval_btn.pack(pady=6)
canvas.pack()
