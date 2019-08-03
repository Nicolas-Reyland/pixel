# GUI functions module
from GUIimage import GUIimage
from CustomTkWidget import CustomTkWidget
from own_utils import float_range
import settings
import gc, os


# defalut value
def init_settings_values():
	global rciibi_color, rciibi_image2

	rciibi_color = settings.settings['rciibi color']
	rciibi_image2 = settings.settings['rciibi image']
	rciibi_tolerance_scale.set(settings.settings['rciibi tolerance'])

	# '/mnt/c/Documents/git_clones/FaceDetect/haarcascade_frontalface_default.xml'
	if not os.path.isfile(settings.settings['cascade file path']):
		# settings.settings['cascade file path'] = '/Users/Nicolas/Documents/git_clone/FaceDetect/haarcascade_frontalface_default.xml'
		# raise FileNotFoundError(settings.settings['cascade file path'])
		messagebox.showwarning('Warning', 'The cascade file could not be found')


onvideo = False
zone_creation_state = -1 # -1: none, 0: in process, 1: finished

last_updated_size = (0,0)
show_error = lambda e: messagebox.showerror('Error ocuured', 'Error Code: {}'.format(e.__class__.__name__))


def update():
	global last_updated_size
	last_updated_size = (0,0)

def change_current_image(arg):
	global resolution_scale, last_opened

	if arg == 'browse':
		filename = filedialog.askopenfilename(
									initialdir=settings.settings['base path'],
									title='Open Image'
									)
		settings.settings['base path'] = filename.replace(os.path.basename(filename), '')
		if filename[-4:] in ['.mp4', '.avi', '.mkv']:
			global source, onvideo, cap
			print('it is a video')
			onvideo = True
			source = pixel.video.Video(filename)
			cap = source.capture()
			return


		if filename:
			try:
				image.change(newimage=pixel.load(filename), type_='file', filename=filename, new=True, function=reset_scalers)
			except:
				messagebox.showerror('Not an Image', '{} could not be read as an image file.'.format(filename))
	elif arg == 'webcam':
		if settings.settings['allow webcam']:
			try:
				image.change(newimage=pixel.cv2.cvtColor(pixel.webcam_shot()[1], pixel.cv2.COLOR_BGR2RGB), type_='webcam shot', new=True, function=reset_scalers)
			except Exception as e:
				show_error(e)
		else:
			messagebox.showerror('Error', 'You have not allowed access to your webcam')
	elif arg == 'face detection': # 							was 1.1 (should be customized inside the GUI)
		image.change(newimage=pixel.detect_object(image.array, scaleFactor=1.2, minNeighbors=5, minSize=(30,30), rectangle_color=(0,255,0), cascade_file_path=settings.settings['cascade file path']),
					 type_='webcam shot',
					 new=False,
					 function=reset_scalers)
	elif arg == 'reset':
		image.to_last_opened()
		reset_scalers()
	elif arg == 'adapt size':
		filename = filedialog.askopenfilename(
									initialdir=settings.settings['base path'],
									title='Adapt to ...'
									)
		if filename:
			try:
				image.change_by_function(lambda array: pixel.adapt_size(array, pixel.load(filename)))
				resolution_scale.set(100)
			except:
				messagebox.showerror('Not an Image', '{} could not be read as an image file.'.format(filename))

	else: # assume it's a function
		try:
			image.change_by_function(arg)
		except Exception as e:
			show_error(e)
	# update anyway
	update()

def rciibi(arg):
	global rciibi_image2, rciibi_image2_backup, rciibi_color, rciibi_tolerance_scale, last_updated_size
	if arg == 'choose image2':
		filename = filedialog.askopenfilename(
									initialdir=settings.settings['base path'],
									title='Choose Background Image for RCiIbI'
									)
		if filename:
			try:
				rciibi_image2 = pixel.load(filename)
				rciibi_image2_backup = rciibi_image2.copy()
			except:
				messagebox.showerror('Not an Image', '{} could not be read as an image file.'.format(filename))
	if arg == 'choose color':
		color = tkcolorpicker.askcolor()
		if color:
			rciibi_color = color[0]
	if arg == 'go':
		try:

			# if the image has a zone
			if image.active_zone:
				# get the equivalent zone (proportions)

				rciibi_zone = image.Zone.clone_to_image(rciibi_image2)
				rciibi_image2 = rciibi_zone.get_zone()

				# resizing rciibi_image2
				rciibi_image2 = image.pixel.resize(rciibi_image2, image.Zone.size()[::-1])

			# if sizes differ
			elif rciibi_image2.shape != image.array.shape:
				rciibi_image2 = pixel.adapt_size(rciibi_image2, image.array)

			# message
			message_frame_label = tk.Label(root, text='')
			message_frame_label.place(relx=.35,rely=.485,relwidth=.3,relheight=.025) # 					 manually re-arranged the time
			message_frame_label['text'] = 'Please wait. Operation should take min {:.1f} seconds'.format(3e-5 * rciibi_image2.shape[0]*rciibi_image2.shape[1])
			root.update()

			# logging
			image.save_to_log('image')

			# apply the function
			image.change_by_function(lambda array: pixel.replace_color_in_image_by_image(array, rciibi_image2, rciibi_color, rciibi_tolerance_scale.get()))

			# reload rciibi_image2
			rciibi_image2 = rciibi_image2_backup.copy()

			# destroy the message
			message_frame_label.destroy()
			del message_frame_label

			# destroy the zone
			rciibi_zone.erase()

		except IndexError:#NameError:
			messagebox.showerror('Missing Parameters', 'Have you selected Image2 or the Color ?')
		update()

def save_current_image():
	filename = filedialog.asksaveasfilename(
								initialdir='/home/valar/Pictures',
								title='Save Image'
								)
	if filename:
		try:
			pixel.save(image.array, filename)
		except:
			messagebox.showerror('Save Error', '{} could not be saved as an image file.'.format(filename))

def clear_current_image():
	image.to_default()
	reset_scalers()

def clear_RAM():
	image.clear_log()
	if settings.settings['clear image when freeing RAM']:
		clear_current_image()
	rciibi_image2 = image.array.copy()
	messagebox.showinfo('RAM cleared', 'The RCiIbI Image2 & the log has been erased')
	get_process_usage()
	# force the python garbage-collector to release unreffered memory
	gc.collect()

def get_process_usage():
	out = os.popen('ps aux | grep {} | grep {}'.format(PID,os.path.realpath(__file__))).read().split('\n')[0]#.split('.')[2][:9]
	#out = os.popen('sudo pmap {}'.format(PID))
	print(out)

def reset_scalers():
	brightness_scale.set(50)
	saturation_scale.set(50)
	contrast_scale.set(1)
	resolution_scale.set(100)

def create_zone():
	global zone_creation_state, select_zone_button_bg, select_zone_button_bg2
	if zone_creation_state == -1:

		if image.active_zone:
			return messagebox.showerror('Error', 'There is already a Zone.\nClick on the "Erase Zone" button\nto be able to create a new one.')

		if zone_creation_state == -1:
			print('Creating zone in GUIf')

			# make the button light red
			select_zone_button_bg = select_zone_button['bg']
			select_zone_button_bg2 = select_zone_button['activebackground']
			select_zone_button['bg'] = pixel.rgb_to_hex(pixel.rgb_color['light_red'])
			select_zone_button['activebackground'] = pixel.rgb_to_hex(pixel.rgb_color['very_light_red'])

			# bind button
			binding = ui.Binding('<Button-1>', image_label, ui.sz.tkcallback)
			binding.bind()
			ui.sz.__binding__ = binding
			ui.sz.init_canvas_creation()

			zone_creation_state = 0

	else:
		print('Zone created in GUIf')

		if len(ui.sz.__ZoneInfo__.nodes) < 3:
			return messagebox.showerror('Zone Error', 'Not enough points to create a polygon (you must have at least 3).')

		zone_creation_state = 1

		# create zone
		ui.sz.gen_zone()
		zone = ui.sz.get_created_canvas()
		zone.init_motion()
		image.active_zone = True
		image.Zone = zone
		image.save_to_log('zone creation')

		# button color, screen update
		select_zone_button['bg'] = select_zone_button_bg
		select_zone_button['activebackground'] = select_zone_button_bg2
		del select_zone_button_bg
		update()

		zone_creation_state = -1

		print('Zone established')


def erase_zone():
	if image.active_zone: # messagebox.askokcancel('Remove Zone', 'Do you really want to remove\nthe current Zone ?')
		# immediately save to log, else the zone is None
		image.save_to_log('zone erasion')
		image.Zone.erase()
		image.Zone = None
		image.active_zone = False
		ui.sz.__Zone__ = None
		ui.sz.__current__ = False
		update()

def crop():
	return messagebox.showwarning('Not Implemented', 'This function has not been implemented yet')
	try:
		assert image.active_zone
		# clear the redo_lgo (new image)
		image.redo_log.clear()
		# save to log
		image.save_to_log('multiple', [('image', image.array), ('zone erasion', image.Zone)])
		# manually change the image
		image.array = image.Zone.get_canvas()
		image.array_backup = image.array.copy()
		erase_work_canvas()
		# set params & update screen
		image.active_zone = False
		print('cropping')
		update()
	except AssertionError:
		messagebox.showerror('Error', 'The current image is not on a Zone.')
	except Exception as e:
		show_error(e)

def add_filter_toplevel():
	global filters
	tmptoplevel = tk.Toplevel()
	tmptoplevel.title('Filters')
	tmptoplevel.attributes('-topmost', 'true')

	filters = {
		'rgb to bgr': ('colorfilter', pixel.cv2.COLOR_RGB2BGR),
		'bgr to grb': ('colorfilter', pixel.cv2.COLOR_BGR2RGB),
		'grayscale': ('colorfilter', pixel.cv2.COLOR_RGB2GRAY),
		'smoothing': ('kernel', pixel.np.ones((5,5),pixel.np.float32)/25),
		'sharpening': ('kernel', pixel.np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])),
		'median filtering': ('function', lambda img: pixel.cv2.medianBlur(img, 5)),
		'bilateral filtering': ('function', lambda img: pixel.cv2.bilateralFilter(img,9,75,75))
	}
	dict_length = len(filters)
	step = 1/dict_length
	for i,rely in float_range(0,1-step,step,enum=True):

		info = list(filters.keys())[i]
		button = CustomTkWidget(tmptoplevel, info, add_filter, popup_onerror=False, **{'text': info})
		button.widget.place(relx=0,rely=rely,relwidth=1,relheight=step)

def add_filter(info):
	global filters
	how_to, core = filters[info]
	if how_to == 'colorfilter':
		image.change_by_function(lambda img: pixel.cv2.cvtColor(img, core))
	elif how_to == 'kernel':
		image.change_by_function(lambda img: pixel.cv2.filter2D(img, -1, core))
	elif how_to == 'function':
		image.change_by_function(core)
	else:
		raise ValueError(f'{how_to} is not a supported image editing type')


def scalers():
	scale_toplevel.deiconify()

def flip_and_rotate():
	flip_and_rotate_toplevel.deiconify()

def grayscale():
	image.change_by_function(lambda array: pixel.cv2.cvtColor(pixel.cv2.cvtColor(array, pixel.cv2.COLOR_RGB2GRAY), pixel.cv2.COLOR_GRAY2RGB))
	update()

def flip(key):
	if key == 'horizontal':
		image.change_by_function(lambda array: pixel.np.array(array[::-1]))
	elif key == 'vertical':
		image.change_by_function(lambda array: pixel.np.array([line[::-1] for line in array]))
	else:
		raise KeyError('{} is not a valid value'.format(key))

def rotate(key):
	if key == 'right':
		image.change_by_function(lambda array: pixel.np.array(pixel.Image.fromarray(array).rotate(-90)))
	elif key == 'left':
		image.change_by_function(lambda array: pixel.np.array(pixel.Image.fromarray(array).rotate(90)))
	else:
		raise KeyError('{} is not a valid value'.format(key))


'''
Settings Ideas:
	- rciibi_color
	- default tolerance (rciibi)
	- base path
	- cascade file path
	- allow webcam
	- save-file-init-dir
	- clear_current_image when free RAM
	- MAX_RAM_USAGE
	- MAX_MEMORY_USAGE
	- CLOSE_PROGRAM_WHEN_MAX_RAM_REACHED
	- CLOSE_PROGRAM_WHEN_MAX_MEM_USAGE_REACHED
	- MAX_LOG_LENGTH
	- clear-log-button
	- smooth_zone - n
	- show debug_button (?)
	- default image (make a copy + 'auto' or 'custom')
	- enable/disable keyboard-shortcuts
	- choose zone-smoothing algorithm (dis/end-able n-selection)
	- default settings button
'''




def smooth_zone():
	image.save_to_log('zone motion')
	image.Zone.update_nodes(image.widg.GUIf.ui.sz.polygon.chaikin_smoothing_algorithm(image.Zone.node_positions(), n=4)) # n controllable by settings
	image.update_function()

def show_usage():
	pass

def debug():
	global rciibi_image2
	try:
		print('shown size',image.get_shown_image().shape)
		print('array size',image.array.shape)
		print('array zone size',image.Zone.size())
		print('rciibi size',rciibi_image2.shape)
	except Exception as e: print(f'An Error occured: {e}')
