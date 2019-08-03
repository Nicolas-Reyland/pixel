# Selection Zone
import numpy as np
import matrix, polygon
from cv2 import line as draw_line
#from own_utils import chronos

__current__ = False # currently creating a zone ?
__ZoneInfo__ = []
__image__ = None
__binding__ = None
__Zone__ = None


# RECODE THE WHOLE THING ?

class Node:
	def __init__(self, position, img_w=1, img_h=1):

		self.position = position
		self.img_w, self.img_h = img_w, img_h
		self.ratio = (self.position[0] / self.img_w, self.position[1] / self.img_h)

	def clone(self):
		return Node(self.position, self.img_w, self.img_h)


class ZoneInfo:

	def __init__(self, image):
		
		self.image = image
		self.width = image.array.shape[0]
		self.height = image.array.shape[1]

		self.nodes = []

	def add_node(self, position):

		position = (int(position[0]), int(position[1]))
		node = Node(position, self.width, self.height)
		self.nodes.append(node)

	def get_rectangle(self, nodes='auto'):
		nodes = self.nodes if nodes == 'auto' else nodes

		positions = [node.position for node in nodes]

		min_x = min(list(map(lambda x: x[0], positions)))
		max_x = max(list(map(lambda x: x[0], positions)))

		min_y = min(list(map(lambda x: x[1], positions)))
		max_y = max(list(map(lambda x: x[1], positions)))

		return (min_x, max_x), (min_y, max_y)

class Zone:

	def __init__(self, ZoneInfo, mode=''):

		# nodes
		self.nodes = ZoneInfo.nodes
		self.node_positions = lambda : [node.position for node in self.nodes]

		self.smoothing_algortithms = {'Chaikin': widg.GUIf.ui.sz.polygon.chaikin,
									  'PAEK': widg.GUIf.ui.sz.polygon.PAEK,
									  'Bezier': widg.GUIf.ui.sz.polygon.bezier}
		self.rectangle = lambda : ZoneInfo.get_rectangle(nodes=self.nodes)

		# current image
		self.image = ZoneInfo.image
		if mode != 'show only':
			self.clear_shown_functions()
			self.valid_positions = polygon.get_valid_positions_v2(self)

		# chronos test
		#print('algorithm1: {}'.format(chronos(lambda : polygon.get_valid_positions(self))))
		#print('algorithm2: {}'.format(chronos(lambda : polygon.get_valid_positions_v2(self))))

		# motion resize initialisation done
		self.motion_init = False

	def size(self):
		# returns the rectangle-size in with the zone lies
		(min_x, max_x), (min_y, max_y) = self.rectangle()
		return (max_x-min_x, max_y-min_y)
	
	def clear_shown_functions(self):
		for key, _ in self.image.shown_functions.items():
			if 'draw_point_' in key:
				self.image.shown_functions.pop(key)
				self.clear_shown_functions()
				break
	
	def update_nodes(self, node_positions):
		self.nodes = [Node(node) for node in node_positions]
		self.normalize_nodes()
	
	def normalize_nodes(self):
		nodes = self.node_positions()
		nodes = list(map(lambda xy: (int(xy[0]), int(xy[1])), nodes))
		self.nodes = [Node(node) for node in nodes]

	def get_zone(self):
		# get the rectangle of the zone on the real image
		(min_x, max_x), (min_y, max_y) = self.rectangle()
		return np.array([line[min_x:max_x] for line in self.image.array[min_y:max_y]])

	def apply_zone(self, canvas, array=None):
		(min_x, max_x), (min_y, max_y) = self.rectangle()
		assert canvas.shape[0] == (max_y - min_y) and canvas.shape[1] == (max_x - min_x)

		if array is None:
			new_array = self.image.array.copy()
		else:
			new_array = array.copy()

		for pos in self.valid_positions:
			try: new_array[pos[1]][pos[0]] = canvas[pos[1]-min_y][pos[0]-min_x]
			except IndexError:
				print(f'index error at pos {pos}')

		return new_array

	def change_zone(self, function, array=None):

		if array is None:
			array = self.get_zone()
		elif array.shape != self.get_zone().shape:
			if array.shape != self.image.array.shape:
				raise ValueError('The given array has not the same size as the zone-rectangle, nor as the zone-image')
			else:
				array = self.clone_to_image(array)

		new_array = array.copy()
		array = function(array)

		for pos in self.valid_positions:
			new_array[pos[0]][pos[1]] = array[pos[0]][pos[1]]

		return new_array

	def show_zone(self, image):

		new_x, new_y = Zone.transform_position(0,0,'real -> shown', ratios=True)

		new_array = image.copy()

		new_nodes = list(map(lambda xy: ( int(new_x*xy.position[0]), int(new_y*xy.position[1]) ), self.nodes))
		for node_index in range(len(new_nodes)):
			new_array = draw_line(image, new_nodes[node_index-1], new_nodes[node_index], widg.GUIf.settings.settings['line color'], widg.GUIf.settings.settings['line thickness'])
		for node in new_nodes:
			new_array = self.draw_point(new_array, node[0], node[1], adapt=False)

		return new_array

	def init_motion(self):

		# move mouse binding
		self.motion_binding = Binding('<B1-Motion>', widg.image_label, self.canvas_callback_motion)
		self.motion_binding.bind()
		# press mouse button binding
		self.press_binding = Binding('<Button-1>', widg.image_label, self.canvas_callback_press)
		self.press_binding.bind()
		# release mouse button binding
		self.release_binding = Binding('<ButtonRelease-1>', widg.image_label, self.canvas_callback_release)
		self.release_binding.bind()
		# padding
		self.padding = 10 # no paddong, only click on the little squares
		# for zone resizing
		self.mouse_on_node = None # node index
		# canvas motion
		self.motion_speed = 2
		self.last_mouse_pos = None
		self.mouse_diff = (0,0)
		self.valid_inside = False # change this (use point_in_polygon function ?)

		self.deprecated = False
		self.motion_init = True

	def unbind_all(self):

		self.motion_binding.unbind()
		self.press_binding.unbind()
		self.release_binding.unbind()

	def canvas_callback_press(self, event):

		(min_x, max_x), (min_y, max_y) = self.rectangle()

		# shown w & h
		shown_width = widg.image_frame.winfo_width()
		shown_height = widg.image_frame.winfo_height()

		# width and height ratios
		width_ratio = self.image.array.shape[1] / shown_width
		height_ratio = self.image.array.shape[0] / shown_height

		# lambdas for new coordinates
		new_x = lambda x: int(width_ratio * (x - 1))
		new_y = lambda y: int(height_ratio * (y - 1))

		# mouse click coordinates on real image
		x = new_x(event.x)
		y = new_y(event.y)

		### check if mouse (first press) is on a node (the gray box <- may change that in settings ?)

		# first click
		if event.type.name == 'ButtonPress':

			for i,node in enumerate(self.nodes):
				node_x, node_y = node.position
				node_x, node_y = Zone.transform_position(node_x, node_y, 'real -> shown')

				node_padding = 4
				mouse_inside_node = node_x-node_padding < event.x < node_x+node_padding and node_y-node_padding < event.y < node_y+node_padding

				if mouse_inside_node:
					self.mouse_on_node = i
					print(f'mouse on node {i}')

					break
			else:
				self.mouse_on_node = None
				print('mouse on no node')

				if polygon.point_in_polygon(self.node_positions(), (x,y), length=max_x - min_x + 1):
					self.valid_inside = True
					self.last_mouse_pos = (x,y)
					self.mouse_diff
				else:
					self.valid_inside = False
					self.mouse_diff = (0,0)
					self.last_mouse_pos = None

			# save zone
			if self.mouse_on_node is not None or self.valid_inside:
				self.image.save_to_log('zone motion', self.clone_nodes())

		elif self.valid_inside:
			self.mouse_diff = matrix.vector.subtract((x,y), self.last_mouse_pos)
			self.last_mouse_pos = (x,y)

		else:
			self.mouse_diff = (0,0)

		# max and min of x,y
		x = min(max(x,0),self.image.array.shape[1])
		y = min(max(y,0),self.image.array.shape[0])

		return x, y


	def canvas_callback_motion(self, event): # NOT DONE

		x, y = self.canvas_callback_press(event)

		# is this a first click or are we in the middle of a motion
		if self.mouse_on_node is not None:
			self.nodes[self.mouse_on_node].position = (x,y)

		if self.valid_inside:

			for node in self.nodes:
				node.position = matrix.vector.add(node.position, self.mouse_diff)
				node.position[0] = min(max(0, node.position[0]), self.image.array.shape[1]) # - 1 ?
				node.position[1] = min(max(0, node.position[1]), self.image.array.shape[0]) # - 1 ?

		self.image.update_function()

	def canvas_callback_release(self, event):
		# setting values to null
		self.valid_inside = False
		self.valid_positions = polygon.get_valid_positions_v2(self)
		print('updated zone')

	def move(self, moveindex):
		# 0: left
		# 1: right
		# 2: up
		# 3: down
		pass

	def clone(self):

		zoneinfo = ZoneInfo(self.image)
		zoneinfo.nodes = self.nodes
		zone = Zone(zoneinfo)

		return zone
	
	def clone_to_image(self, image):

		w_ratio, h_ratio = Zone.transform_position(0,0,'real -> custom',ratios=True,image=image)
		zoneinfo = ZoneInfo(widg.GUIf.GUIimage(image, 0, 0, volatile=True))

		nodes = self.node_positions()
		nodes = list(map(lambda xy: (xy[0]*w_ratio, xy[1]*h_ratio), nodes))

		for node in nodes:
			zoneinfo.add_node(node)

		zone = Zone(zoneinfo, 'show only')

		return zone

	def clone_nodes(self):
		return [node.clone() for node in self.nodes]
	
	def remove_double_nodes(self):
		nodes = self.node_positions()
		nodes = list(map(lambda xy: (int(xy[0]), int(xy[1])), nodes))
		nodes = list(set(nodes))
		self.nodes = [Node(node) for node in nodes]

	def smooth(self):
		self.image.save_to_log('motion')
		algorithm = self.smoothing_algortithms[widg.GUIf.settings.settings['smoothing algorithm']]
		if widg.GUIf.settings.settings['smoothing algorithm'] == 'Chaikin':
			new_nodes = algorithm(self.image.Zone.node_positions(), n=widg.GUIf.settings.settings['smooth var'])
		else:
			new_nodes = algorithm(self.image.Zone.node_positions())
		self.image.Zone.update_nodes(new_nodes)
		self.image.update_function()













	def erase(self):
		global __current__, __image__, __Canvas__
		if self.motion_init: self.unbind_all()
		__current__ = False
		__binding__ = None
		__Zone__ = None
		__ZoneInfo__ = None


	@staticmethod
	def transform_position(x, y, key, ratios=False, image=None):
		global __image__
		if image is not None:
			assert hasattr(image, 'shape')
		shown_h, shown_w = widg.image_frame.winfo_height(), widg.image_frame.winfo_width()
		real_w, real_h = __image__.array.shape[1], __image__.array.shape[0]
		if key == 'shown -> real':
			width_ratio = real_w / shown_w
			height_ratio = real_h / shown_h
		elif key == 'real -> shown':
			width_ratio = shown_w / real_w
			height_ratio = shown_h / real_h
		elif ' -> custom' in key:
			key = key.replace(' -> custom', '')
			if key == 'real':
				width_ratio = image.shape[1] / real_w
				height_ratio = image.shape[0] / real_h
			elif key == 'shown':
				width_ratio = image.shape[1] / shown_w
				height_ratio = image.shape[0] / shown_h
			else:
				raise NameError(f'Wrong key: {key}')
		elif 'custom -> ' in key:
			key = key.replace('custom -> ', '')
			if key == 'real':
				width_ratio = real_w / image.shape[1]
				height_ratio = real_h / image.shape[0]
			elif key == 'shown':
				width_ratio = shown_w / image.shape[1]
				height_ratio = shown_h / image.shape[0]
			else:
				raise NameError(f'Wrong key: {key}')
		else:
			raise NameError(f'Wrong key: {key}')

		if ratios:
			return width_ratio, height_ratio

		x *= width_ratio
		y *= height_ratio
		return x, y

	@staticmethod
	def draw_point(image, x, y, adapt=True):

		intern_node_color = widg.GUIf.settings.settings['intern node color']
		extern_node_color = widg.GUIf.settings.settings['extern node color']

		if adapt:

			shown_h, shown_w = widg.image_frame.winfo_height(), widg.image_frame.winfo_width()

			width_ratio = image.shape[1] / shown_w
			height_ratio = image.shape[0] / shown_h

			diff_x = 4 * width_ratio # 4 -> 2 on right, 2 on left (central is always drawn)
			diff_y = 4 * height_ratio

			from_x = int(x - diff_x / 2)
			to_x = int(x + diff_x / 2) + 1
			from_y = int(y - diff_y / 2)
			to_y = int(y + diff_y / 2) + 1

			new_array = image.copy()

			# --- draw a 5x5 px (normal) square around click ---

			# inside
			for x in range(from_x,to_x):
				for y in range(from_y,to_y):
					if image.shape[1] > x >= 0 and image.shape[0] > y >= 0:
						new_array[y][x] = intern_node_color
			# up & down exterior line
			for x in range(from_x-1,to_x+1):
				if image.shape[1] > x >= 0 and image.shape[0] > from_y-1 >= 0: new_array[from_y-1][x] = extern_node_color
				if image.shape[1] > x >= 0 and image.shape[0] > to_y+1 >= 0: new_array[to_y+1][x] = extern_node_color
			# right & left lines
			for y in range(from_y,to_y,1):
				if image.shape[1] > to_x+1 and from_x-1 >= 0 and image.shape[0] > y >= 0:
					new_array[y][from_x-1] = extern_node_color
					new_array[y][to_x+1] = extern_node_color

		else: # not adapt

			from_x = x - 2
			to_x = x + 2 + 1
			from_y = y - 2
			to_y = y + 2 + 1

			new_array = image.copy()

			# --- draw a 5x5 px (normal) square around click ---

			# inside
			for x in range(from_x,to_x):
				for y in range(from_y,to_y):
					if image.shape[1] > x >= 0 and image.shape[0] > y >= 0:
						new_array[y][x] = intern_node_color
			# up & down max_xterior line
			for x in range(from_x-1,to_x+1):
				if image.shape[1] > x >= 0 and image.shape[0] > from_y-1 >= 0: new_array[from_y-1][x] = extern_node_color
				if image.shape[1] > x >= 0 and image.shape[0] > to_y+1 >= 0: new_array[to_y+1][x] = extern_node_color
			# right & left lines
			for y in range(from_y,to_y,1):
				if image.shape[1] > to_x+1 and from_x-1 >= 0 and image.shape[0] > y >= 0:
					new_array[y][from_x-1] = extern_node_color
					new_array[y][to_x+1] = extern_node_color

		return new_array





def init_canvas_creation():
	# very dirty, I know
	global __current__, __ZoneInfo__, __image__, __binding__, __Canvas__
	__current__ = True
	__ZoneInfo__ = ZoneInfo(__image__)
	__Canvas__ = 'No max_xisting Canvas(2)'
	if not __binding__.active:
		__binding__.bind()

def tkcallback(event):
	global __current__, __image__, __ZoneInfo__
	# get x and y position of click on image
	x,y = Zone.transform_position(event.x,event.y,'shown -> real')
	# draw point on image while creating zone
	point_index = len(__ZoneInfo__.nodes)
	if point_index == 1:
		__image__.add_shown_function(f'draw_point_{point_index}', lambda array: Zone.draw_point(array, int(Zone.transform_position(x,0,'real -> shown')[0]), int(Zone.transform_position(0,y,'real -> shown')[1]), adapt=False))
	elif point_index == 2:
		__image__.add_shown_function(f'draw_point_{point_index}', lambda array: Zone.draw_point(array, int(Zone.transform_position(x,0,'real -> shown')[0]), int(Zone.transform_position(0,y,'real -> shown')[1]), adapt=False))
		__image__.add_shown_function(f'draw_point_{point_index}_line', lambda array: draw_line(array, __ZoneInfo__.nodes[0].position, __ZoneInfo__.nodes[1].position, widg.GUIf.settings.settings['line color'], widg.GUIf.settings.settings['line thickness']))
	else:
		__image__.add_shown_function(f'draw_point_{point_index}', lambda array: Zone.show_zone(Zone(__ZoneInfo__, 'show only'), __image__.shown_image))
	__image__.update_function()
	# add this position to the ZoneInfo
	print('adding node at {}'.format((x,y)))
	__ZoneInfo__.add_node((x,y))
	#create the zone
	if widg.GUIf.zone_creation_state == 1:
		__current__ = False
		__binding__.unbind()
		__Zone__ = Zone(__ZoneInfo__)
		print('[z!] Zone Created')

def gen_zone():
	global __Zone__, __ZoneInfo__
	__Zone__ = Zone(__ZoneInfo__)

def get_created_canvas():
	if widg.GUIf.zone_creation_state == 1:
		global __Zone__
		return __Zone__
	else:
		raise ValueError('Zone doesn\'t seem finished')


