#!/bin/python3
# Pixel library GUI

# Gui Programming
import tkinter as tk
import user_input as ui
import widgets as widg
pixel = widg.pixel

# init settings
widg.GUIf.settings.init()
# set some values from settings in GUIf
widg.GUIf.init_settings_values()
# give widg to settings module
widg.GUIf.settings.widg = widg

# for further resizing, etc.
widg.root.update()
widg.base_root_dimensions = (widg.root.winfo_screenwidth(), widg.root.winfo_screenheight())
widg.base_root_coordinates = (widg.root.winfo_x(), widg.root.winfo_y())

if widg.GUIf.settings.settings['fullscreen']:

	widg.root.overrideredirect(True)
	widg.root.attributes('-fullscreen', True)
	widg.root.geometry('{0}x{1}+{2}+{3}'.format(widg.root.winfo_screenwidth(), widg.root.winfo_screenheight(), 0, 0))
	#widg.GUIf.settings.showwarning('Warning', 'Fullscreen not preoperly implemented')
	#widg.root.focus_force()
	widg.root.focus_set()
	#widg.root.wm_state('normal')
	print('setting fullscreen')


# Image
from PIL import ImageTk

# Memory
from psutil import virtual_memory
import resource

# side-dependencies
import time, sys, os, threading

# icon
#widg.root.tk.call('wm', 'iconphoto', widg.root._w, ImageTk.PhotoImage(file='icon.ico'))#'data/icon.ico'))

settings = widg.GUIf.settings
PID = os.getpid()

main_loop = True
widg.GUIf.widg = widg
widg.GUIf.ui = ui
widg.GUIf.PID = PID

# init image
if not widg.GUIf.settings.settings['use custom default image']:
	from random import choice
	poss_images = ['bgr_rgb', 'disturbing_blur', 'polygon_trick', 'sharpened', 'super_cool', 'ultra_blur']
	widg.GUIf.image = widg.GUIf.GUIimage(pixel.load('data/no_image_loaded_{}.jpg'.format(choice(poss_images))), widg, widg.GUIf.update)
else:
	widg.GUIf.image = widg.GUIf.GUIimage(pixel.load(widg.GUIf.settings.settings['default image']), widg, widg.GUIf.update)
image = widg.GUIf.image

widg.init_GUIf()

# ui
ui.image = image
ui.widg = widg
ui.sz.tk = tk
ui.sz.widg = widg
ui.init()

# --- Main loop ---
def main():

	widg.root.update()
	widg.GUIf.clear_current_image()

	widg.image_label['image'] = ImageTk.PhotoImage(image=pixel.Image.fromarray(widg.GUIf.image.array))

	last_brightness = widg.brightness_scale.get()
	last_saturation = widg.saturation_scale.get()
	last_contrast = widg.contrast_scale.get()
	last_resolution = widg.resolution_scale.get()

	# warnings
	max_memory_usage_allowed_exceeded = False
	max_ram_usage_exceeded = False

	ui.handle_events()

	while main_loop:

		# update some parameters
		widg.root.update()

		# set the shown image
		image.shown_image = image.array.copy()

		# --- Image Frame ---
		image_widget_size = (widg.image_frame.winfo_height(), widg.image_frame.winfo_width())

		# ----- Scales -----
		if widg.saturation_scale.get() != last_saturation or widg.resolution_scale.get() != last_resolution or widg.brightness_scale.get() != last_brightness or widg.contrast_scale.get() != last_contrast:

			brightness_ratio = int(((widg.brightness_scale.get() * 2) / 100 - 1) * 255 / 2)
			saturation_ratio = int(((widg.saturation_scale.get() * 2) / 100 - 1) * 255 / 2)
			contrast_ratio = widg.contrast_scale.get()
			resolution_ratio = widg.resolution_scale.get() / 100 / 2

			# first resize (so the other operations won't take as much time)
			current_image_modify = pixel.resize(image.array_backup, (int(image.array_backup.shape[0]*resolution_ratio),int(image.array_backup.shape[1]*resolution_ratio)))
			if widg.brightness_scale.get() != 50: current_image_modify = pixel.brightness(current_image_modify, brightness_ratio) # it's too long to be done every time
			current_image_modify = pixel.np.array(pixel.ImageEnhance.Contrast(pixel.Image.fromarray(current_image_modify)).enhance(contrast_ratio))
			current_image_modify = pixel.saturation(current_image_modify, saturation_ratio)

			# update shoen_image
			image.shown_image = current_image_modify.copy()

			# update label
			widg.IF_image_size_label['text'] = '{} x {} (shown: {} x {})'.format(image.array.shape[0],image.array.shape[1],image.shown_image.shape[1],image.shown_image.shape[0])

			# save all params
			last_brightness = widg.brightness_scale.get()
			last_saturation = widg.saturation_scale.get()
			last_contrast = widg.contrast_scale.get()
			last_resolution = widg.resolution_scale.get()

			widg.GUIf.update()

		# --- Show Image ---
		if image_widget_size != widg.GUIf.last_updated_size:
			# get a new image
			shown_image = image.get_shown_image()
			shown_image = ImageTk.PhotoImage(image=pixel.Image.fromarray(shown_image))
			# update the image
			widg.image_label['image'] = shown_image
			# update the widg.GUIf.last_updated_size
			widg.GUIf.last_updated_size = image_widget_size
			# update label
			widg.IF_image_size_label['text'] = '{} x {} (shown: {} x {})'.format(image.array.shape[0],image.array.shape[1],image.shown_image.shape[1],image.shown_image.shape[0])


		# --- Memory ---
		RAM_percent = virtual_memory().percent
		self_memory_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024

		# update label
		widg.RAM_label['text'] = 'Used RAM: {} %\nMemory: {:.1f} Mb'.format(RAM_percent, self_memory_usage)

		# self memory usage
		if self_memory_usage > settings.settings['max Memory usage'] and not max_memory_usage_allowed_exceeded:
			widg.messagebox.showwarning('Warning', 'The process has exceeded the\nmax allowed memory usage!\nUsage: {:.1f} Mb, Max allowed: {} Mb'.format(self_memory_usage, settings.settings['max Memory usage']))
			max_memory_usage_allowed_exceeded = True
			if settings.settings['close program when max Memory exceeds']:
				sys.exit('Memory usage has been exceeded at {:.3f} Mb! (Max was {}) Exiting'.format(float(self_memory_usage), settings.settings['max Memory usage']))

		# RAM usage (percent)
		if RAM_percent > settings.settings['max RAM usage'] and not max_ram_usage_exceeded:
			if not settings.settings['close program when max RAM exceeds']: widg.messagebox.showwarning('Warning', 'The maximum RAM percentage {}% has been exceeded at {}% !'.format(settings.settings['max RAM usage'], RAM_percent))
			max_ram_usage_exceeded = True
			if settings.settings['close program when max RAM exceeds']:
				sys.exit('RAM usage exceeded at {}%! (Max was {}) Exiting'.format(RAM_percent, settings.settings['max RAM usage']))

		# check log length
		image.check_log(settings.settings['max log length'])


		# if widg.GUIf.onvideo:
		# 	image.array = pixel.cv2.cvtColor(widg.GUIf.cap.read()[1], pixel.cv2.COLOR_RGB2BGR)
		# 	widg.GUIf.last_updated_size = (0,0)



# set_params functions for widg
def set_params():

	brightness_ratio = int(((widg.brightness_scale.get() * 2) / 100 - 1) * 255 / 2)
	saturation_ratio = int(((widg.saturation_scale.get() * 2) / 100 - 1) * 255 / 2)
	contrast_ratio = widg.contrast_scale.get()
	resolution_ratio = widg.resolution_scale.get() / 100 / 2

	# first resize (so the other operations won't take as much time)
	current_image_modify = pixel.resize(image.array_backup, (int(image.array_backup.shape[0]*resolution_ratio),int(image.array_backup.shape[1]*resolution_ratio)))
	current_image_modify = pixel.brightness(current_image_modify, brightness_ratio)
	current_image_modify = pixel.np.array(pixel.ImageEnhance.Contrast(pixel.Image.fromarray(current_image_modify)).enhance(contrast_ratio))
	current_image_modify = pixel.saturation(current_image_modify, saturation_ratio)

	# clear redo log
	image.redo_log.clear()
	# save to log
	image.save_to_log('image')
	# manually change the image
	image.array = current_image_modify
	image.array_backup = current_image_modify.copy()

	# update & reset
	image.update_function()
	widg.GUIf.reset_scalers()

# some widg handling
widg.set_params = set_params
# init some functions
widg.init()
widg.scale_toplevel.protocol('WM_DELETE_WINDOW', widg.scale_toplevel.withdraw)
widg.flip_and_rotate_toplevel.protocol('WM_DELETE_WINDOW', widg.flip_and_rotate_toplevel.withdraw)


def show_RAM():
	global main_loop
	while main_loop:
		#print('Used RAM: {} % - Process in Memory: {} Mb'.format(virtual_memory().percent, resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024))
		out = int(os.popen('ps aux | grep {} | grep {}'.format(PID,os.getcwd())).read().split('\n')[0].split('.')[2][2:9])
		print('Memory used: {}'.format(out))
		time.sleep(2)

#threading.Thread(target=show_RAM).start()


if __name__ == '__main__':
	try:
		main()
	except tk.TclError:
		main_loop = False
		# percentage of used RAM
		print('Leaving at {} % RAM'.format(virtual_memory().percent))

'''
TODO :
 - keyboard shortcuts																		DONE
 - cut image (pixel)																		DONE
 - better save function																		DONE
 - only work on image-parts																	DONE
 - better undo/redo																			DONE
 - more scalers (in a separate window?), like contrast, etc.								DONE
 - zooming
 - rescale canvas with mouse-drag															DONE
 - video editing (different project maybe ?/different modes ?)
 - flip image (why not done yet?)															DONE
 - merge images (think of horizontal partial, maybe in diagonal)
 - nice help window
 - polygonial canvas																		DONE
 - multi-canvas working
 - drawing, etc.
 - unnatural (more than normally possible) zooming with neural netowrks
 - styling with neural networks
 - work with objects on the image
 - move canvas around																		DONE
 - settings (go through every fcking varaible and, if possible, add to settings)
 - zone rotation
 - windows/linux arangement (think ctrl+ shortcuts)											URGENT

REALLY COOL:
 - sharpen the image																		DONE
 - filters like RGB -> BGR																	DONE

TO FIX:
 - crop
 - some weird bug with undo/redo (try to spam to reproduce (zones were in there ?))

'''

