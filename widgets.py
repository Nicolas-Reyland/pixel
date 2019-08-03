# Tkinter widgets
import tkinter as tk
from tkinter import filedialog, messagebox
import tkcolorpicker
import GUI_functions as GUIf
import pixel
# texts for 
from help import texts

GUIf.messagebox = messagebox

WIDTH = 1200
HEIGHT = 800

# setup root
root = tk.Tk()
root.title('PiGui')

# set the window size
tk.Canvas(root,height=HEIGHT,width=WIDTH).pack()

# Bar Frame
bar_frame_bg = pixel.rgb_to_hex((240,240,240))
bar_frame = tk.Frame(root, bg=bar_frame_bg)
bar_frame.place(x=0,y=0,relwidth=1,relheight=.05)
GUIf.bar_frame = bar_frame

# --- Buttons ---
open_button = tk.Button(bar_frame, bg=bar_frame_bg, text='Open', command=lambda : GUIf.change_current_image('browse'))
open_button.place(relwidth=.1,relheight=1)

save_button = tk.Button(bar_frame, bg=bar_frame_bg, text='Save', command=GUIf.save_current_image)
save_button.place(relx=.105,relwidth=.1,relheight=1)

help_button = tk.Button(bar_frame, bg=bar_frame_bg, text='Help', command=GUIf.show_usage)
help_button.place(relx=.21,relwidth=.1,relheight=1)

settings_button = tk.Button(bar_frame, bg=bar_frame_bg, text='Settings', command=GUIf.settings.show_toplevel)
settings_button.place(relx=.315,relwidth=.1,relheight=1)

close_button = tk.Button(bar_frame, bg=bar_frame_bg, text='Close', command=GUIf.clear_current_image)
close_button.place(relx=.9,relwidth=.1,relheight=1)


# Image Frame
image_frame = tk.Frame(root)
image_frame.place(relx=.1,rely=.05,relwidth=.8,relheight=.9)
GUIf.image_frame = image_frame


# Toplevel
scale_toplevel = tk.Toplevel(width=200,height=300) # might pimp those
GUIf.scale_toplevel = scale_toplevel

flip_and_rotate_toplevel = tk.Toplevel(width=300,height=200)
GUIf.flip_and_rotate_toplevel = flip_and_rotate_toplevel

# Toplevel: inside
brightness_scale = tk.Scale(scale_toplevel, from_=0, to=100, label='brightness', orient=tk.HORIZONTAL, resolution=.1)
brightness_scale.place(rely=0,relwidth=1,relheight=.2)
brightness_scale.set(50)
GUIf.brightness_scale = brightness_scale

saturation_scale = tk.Scale(scale_toplevel, from_=0, to=100, label='saturation', orient=tk.HORIZONTAL, resolution=.1)
saturation_scale.place(rely=.25,relwidth=1,relheight=.2)
saturation_scale.set(50)
GUIf.saturation_scale = saturation_scale

contrast_scale = tk.Scale(scale_toplevel, from_=0, to=5, label='contrast', orient=tk.HORIZONTAL, resolution=.05)
contrast_scale.place(rely=.5,relwidth=1,relheight=.2)
contrast_scale.set(1)
GUIf.contrast_scale = contrast_scale

resolution_scale = tk.Scale(scale_toplevel, from_=5, to=100, label='resolution', orient=tk.HORIZONTAL, resolution=.1)
resolution_scale.place(rely=.75,relwidth=1,relheight=.2)
resolution_scale.set(100)
GUIf.resolution_scale = resolution_scale


flip_horizontal_button = tk.Button(flip_and_rotate_toplevel, text='Flip H', command=lambda : GUIf.flip('horizontal'))
flip_horizontal_button.place(relx=.01,rely=.01,relwidth=.485,relheight=.48)

flip_vertical_button = tk.Button(flip_and_rotate_toplevel, text='Flip V', command=lambda : GUIf.flip('vertical'))
flip_vertical_button.place(relx=.505,rely=.01,relwidth=.485,relheight=.48)

rotate_right_button = tk.Button(flip_and_rotate_toplevel, text='Rotate R', command=lambda : GUIf.rotate('right'))
rotate_right_button.place(relx=.01,rely=.51,relwidth=.485,relheight=.48)

rotate_left_button = tk.Button(flip_and_rotate_toplevel, text='Rotate L', command=lambda : GUIf.rotate('left'))
rotate_left_button.place(relx=.505,rely=.51,relwidth=.485,relheight=.48)


# Toplevel: Titles and withdraw
scale_toplevel.title('Scalers')
scale_toplevel.withdraw()

flip_and_rotate_toplevel.title('Flip & Rotate')
flip_and_rotate_toplevel.withdraw()



# Stat Frame
stat_frame_bg = pixel.rgb_to_hex((197,207,230))
stat_frame = tk.Frame(root, bg=stat_frame_bg)
stat_frame.place(x=0,rely=.05,relwidth=.1,relheight=.95)
stat_frame_label = tk.Label(stat_frame, text='', bg=stat_frame_bg, font='Times 18 bold') # Stats
stat_frame_label.place(rely=.005,relwidth=1,relheight=.05)

scalers_button = tk.Button(stat_frame, text='Scalers', command=GUIf.scalers)
scalers_button.place(rely=.06,relwidth=1,relheight=.05)
GUIf.scalers_button = scalers_button

# set_params button in init()

adapt_size_button = tk.Button(stat_frame, text='Adapt Size', command=lambda : GUIf.change_current_image('adapt size'))
adapt_size_button.place(rely=.17,relwidth=1,relheight=.05)

crop_button = tk.Button(stat_frame, text='Crop', command=GUIf.crop)
crop_button.place(rely=.225,relwidth=1,relheight=.05)

flip_and_rotate_button = tk.Button(stat_frame, text='Flip & Rotate', command=GUIf.flip_and_rotate)
flip_and_rotate_button.place(rely=.28,relwidth=1,relheight=.05)

# sharpen_button = tk.Button(stat_frame, text='Sharpen', command=lambda : GUIf.image.change_by_function(pixel.sharpen))
# sharpen_button.place(rely=.335,relwidth=1,relheight=.05)

add_filter_button = tk.Button(stat_frame, text='Add Filter', command=GUIf.add_filter_toplevel)
add_filter_button.place(rely=.335,relwidth=1,relheight=.05)

debug_button = tk.Button(stat_frame, text='Debug', command=GUIf.debug)
debug_button.place(rely=.69,relwidth=1,relheight=.05)

select_zone_button = tk.Button(stat_frame, text='Select Zone', command=GUIf.create_zone)
select_zone_button.place(rely=.745,relwidth=1,relheight=.05)
GUIf.select_zone_button = select_zone_button

erase_zone_button = tk.Button(stat_frame, text='Erase Zone', command=GUIf.erase_zone)
erase_zone_button.place(rely=.8,relwidth=1,relheight=.05)



RAM_label = tk.Label(stat_frame, text='', bg=stat_frame_bg)
RAM_label.place(relx=0,rely=.89,relwidth=1,relheight=.05)
GUIf.RAM_label = RAM_label

clear_RAM_button = tk.Button(stat_frame, text='Free up RAM',command=GUIf.clear_RAM)
clear_RAM_button.place(relx=0,rely=.945,relwidth=1,relheight=.05)


# Tool Frame
tool_frame_bg = pixel.rgb_to_hex((197,207,230))
tool_frame = tk.Frame(root, bg=tool_frame_bg)
tool_frame.place(relx=.9,rely=.05,relwidth=.1,relheight=.95)
tool_bar_label = tk.Label(tool_frame, text='', bg=tool_frame_bg, font='Times 18 bold') # Tools
tool_bar_label.place(rely=.005,relwidth=1,relheight=.05)

webcam_shot_button = tk.Button(tool_frame, text='Webcam Shot', command=lambda : GUIf.change_current_image('webcam'))
webcam_shot_button.place(rely=.06,relwidth=1,relheight=.05)

detect_object_button = tk.Button(tool_frame, text='Detect Faces', command=lambda : GUIf.change_current_image('face detection'))
detect_object_button.place(rely=.115,relwidth=1,relheight=.05)

horizontal_partial_button = tk.Button(tool_frame, text='H Partial', command=lambda : GUIf.change_current_image(pixel.horizontal_partial))
horizontal_partial_button.place(rely=.17,relwidth=1,relheight=.05)

vertical_partial_button = tk.Button(tool_frame, text='V Partial', command=lambda : GUIf.change_current_image(pixel.vertical_partial))
vertical_partial_button.place(rely=.225,relwidth=1,relheight=.05)

grayscale_button = tk.Button(tool_frame, text='Grayscale', command=GUIf.grayscale)
grayscale_button.place(rely=.28,relwidth=1,relheight=.05)

# RCiIbI (Replace Coor in Image by Image)
rciibi_label = tk.Label(tool_frame, text='RCiIbI', bg=tool_frame_bg)
rciibi_label.place(rely=.335,relwidth=1,relheight=.05)

rciibi_choose_button = tk.Button(tool_frame, text='Image 2', command=lambda : GUIf.rciibi('choose image2'))
rciibi_choose_button.place(relx=.05,rely=.39,relwidth=.9,relheight=.05)

rciibi_color_button = tk.Button(tool_frame, text='Color', command=lambda : GUIf.rciibi('choose color'))
rciibi_color_button.place(relx=.05,rely=.445,relwidth=.9,relheight=.05)

rciibi_tolerance_scale = tk.Scale(tool_frame, from_=0, to=255, label='tolerance', orient=tk.HORIZONTAL)
rciibi_tolerance_scale.place(relx=.05,rely=.5,relwidth=.9,relheight=.06)
GUIf.rciibi_tolerance_scale = rciibi_tolerance_scale

rciibi_go_button = tk.Button(tool_frame, text='Go', command=lambda : GUIf.rciibi('go'))
rciibi_go_button.place(relx=.05,rely=.565,relwidth=.9,relheight=.05)


def init():
	global undo_button, redo_button
	undo_button = tk.Button(tool_frame, text='Undo', command=GUIf.image.undo)
	undo_button.place(relx=0,rely=.835,relwidth=1,relheight=.05)

	redo_button = tk.Button(tool_frame, text='Redo', command=GUIf.image.redo)
	redo_button.place(relx=0,rely=.89,relwidth=1,relheight=.05)

	set_params_button = tk.Button(stat_frame, text='Set Scalers', command=set_params)
	set_params_button.place(rely=.115,relwidth=1,relheight=.05)



reset_button = tk.Button(tool_frame, text='Reset', command=lambda : GUIf.change_current_image('reset'))
reset_button.place(relx=0,rely=.945,relwidth=1,relheight=.05)

# Info Frame
info_frame_bg = pixel.rgb_to_hex((190,190,190))
info_frame = tk.Frame(root, bg=info_frame_bg)
info_frame.place(relx=.1,rely=.95,relwidth=.8,relheight=.05)

IF_image_size_label = tk.Label(info_frame, bg=info_frame_bg, text='no shape')
IF_image_size_label.place(relx=0,rely=0,relwidth=.3,relheight=1)
GUIf.IF_image_size_label = IF_image_size_label

IF_image_location_label = tk.Label(info_frame, bg=info_frame_bg, text='default')
IF_image_location_label.place(relx=.3,rely=0,relwidth=.4,relheight=1)
GUIf.IF_image_location_label = IF_image_location_label

IF_opened_at_label = tk.Label(info_frame, bg=info_frame_bg, text='opened at ---')
IF_opened_at_label.place(relx=.7,rely=0,relwidth=.3,relheight=1)
GUIf.IF_opened_at_label = IF_opened_at_label

image_label = tk.Label(image_frame)
image_label.place(relwidth=1,relheight=1)
GUIf.image_label = image_label

# run this at start
def init_GUIf():

	GUIf.tk = tk
	GUIf.root = root
	GUIf.pixel = pixel
	GUIf.filedialog, GUIf.messagebox, GUIf.tkcolorpicker = filedialog, messagebox, tkcolorpicker

	GUIf.clear_current_image()

def invisible(frame):
	frame.wait_visibility(frame)
	frame.wm_attributes('-alpha', .3)
	return frame
