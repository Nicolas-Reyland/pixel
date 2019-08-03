# User input
import selection_zone as sz

class Binding:

	def __init__(self, name, frame, callback):

		self.name = name
		self.frame = frame
		self.callback = callback

		self.active = False
		self.funcid = None

	def bind(self):
		self.funcid = self.frame.bind(self.name, self.callback)
		self.active = True

	def unbind(self):
		if self.active:
			self.frame.unbind(self.name, self.funcid)
			self.active = False


def init():

	sz.__image__ = image
	sz.widg = widg
	sz.Binding = Binding


def handle_events():
	global keyboard_shortcuts_binding

	# keyboard shortcuts
	keyboard_shortcuts_binding = Binding('<Key>', widg.root, keyboard_shortcuts)

	if widg.GUIf.settings.settings['use keyboard shortcuts']:
		keyboard_shortcuts_binding.bind()


# Callbacks

def get_image_index_by_event(event):

	widget_size = (widg.image_frame.winfo_height(), widg.image_frame.winfo_width())
	
	x_index = int(widg.GUIf.image.array.shape[1] / widget_size[1] * (event.x - 1))
	y_index = int(widg.GUIf.image.array.shape[0] / widget_size[0] * (event.y - 1))

	new_image = sz.Zone.draw_point(widg.GUIf.image.array, event.x, event.y)

	widg.GUIf.image.shown_image = new_image
	widg.GUIf.update()

def keyboard_shortcuts(event):
	global keyboard_shortcuts_binding
	# print(event.char, event.keycode, event.keysym, event.keysym_num, event.num, event.serial, event.type, event.delta, event.state)

	# q: 24
	# a: 38
	# y: 52
	# numbers: the number (even 0) (diff keysym for numpad: "keysym = number" for numbers, "keysym = KP_number" for numpad)
	# control_l: 37, control_r: 105
	# shift_l: 50, shift_r: 62

	char = event.char
	keycode = event.keycode

	# Control+...
	if keycode == 32 and char != 'o': # ope file
		widg.GUIf.change_current_image('browse')
	elif keycode == 39 and char != 's': # save file
		widg.GUIf.save_current_image()
	elif keycode == 27 and char != 'r': # rciibi
		widg.GUIf.rciibi('go')
	elif keycode == 25 and char != 'w': # close
		widg.GUIf.clear_current_image()
	elif keycode == 43 and char != 'h': # help
		widg.GUIf.show_usage()

	# Simpe key presses
	elif char == 's': # select zone
		widg.GUIf.create_zone()
	elif char == 'e': # erase zone
		widg.GUIf.erase_zone()
	elif char == 'u': # undo
		image.undo()
	elif char == 'r': # redo
		image.redo()
	elif char == 'i': # choose rciibi image2
		widg.GUIf.rciibi('choose image2')
	elif char == 'c': # crop
		widg.GUIf.crop()
	elif char == 'g': # grayscale image
		widg.GUIf.grayscale()
	elif char == 'd': # debug (manually, here)
		print(len(image.Zone.valid_positions))
	elif char == 't': #test (manually, here)
		widg.GUIf.smooth_zone()
		widg.GUIf.image.Zone.remove_double_nodes()

	# special key presses
	elif keycode == 83: # move Zone to the left
		if image.active_zone: image.Zone.move(0)
	elif keycode == 85: # move Zone to the right
		if image.active_zone: image.Zone.move(1)
	elif keycode == 80: # move Zone to up
		if image.active_zone: image.Zone.move(2)
	elif keycode == 88: # move Zone to down
		if image.active_zone: image.Zone.move(3)
	

