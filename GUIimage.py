# Image Class
import datetime

class GUIimage:

	def __init__(self, image, widg, update_function, volatile=False):

		self.array = image.copy()
		self.volatile = volatile

		if not self.volatile: # everything that takes unecessary memory or uses a module link
			self.array_backup = image.copy()
			self.last_opened = image.copy()

			self.shown_image = image.copy()

			self.default = image.copy()
			self.widg = widg
			self.pixel = widg.pixel
			self.update_function = update_function
			self.shown_functions = {}

			self.log = []
			self.redo_log = []

			self.save_to_log = lambda info, value=None: self.log.append((info, self.get_log_value(info) if value is None else value))
			self.add_shown_function = lambda name,function: self.shown_functions.update([[name, function]])

		# working zone
		self.active_zone = False
		self.Zone = None

	def get_shown_image(self):
		# resize to widget
		self.shown_image = self.pixel.resize(self.shown_image, (self.widg.image_frame.winfo_height(), self.widg.image_frame.winfo_width()))

		for _, function in self.shown_functions.items():
			self.shown_image = function(self.shown_image)

		if self.active_zone:
			# show the working zone
			self.shown_image = self.Zone.show_zone(self.shown_image)

		return self.shown_image

	def mini_change(self, newimage):

		self.array = newimage
		self.array_backup = newimage.copy()

	def change(self, newimage, type_, filename=None, new=False, function=None, logging=True):

		if logging: self.save_to_log('image')
		self.mini_change(newimage)

		self.widg.IF_image_size_label['text'] = '{} x {} (shown: {} x {})'.format(self.array.shape[0],self.array.shape[1],self.widg.image_frame.winfo_height(),self.widg.image_frame.winfo_width())
		if type_ == 'file':
			# adapt this to widget size
			self.widg.IF_image_location_label['text'] = filename if len(filename) < 40 else '...' + filename[-30:]
		else:
			self.widg.IF_image_location_label['text'] = type_
		if new:
			self.widg.IF_opened_at_label['text'] = 'opened at {}'.format(str(datetime.datetime.now()).split()[1].split('.')[0])
			self.last_opened = self.array.copy()
			self.redo_log = []
			# if a zone is active, erase it (it's a new picture)
			if self.active_zone:
				self.active_zone = False
				self.Zone.erase()

		if function is not None:
			function()
		self.update_function()

	def change_by_function(self, function, logging=True):
		ancient = self.array.copy()
		if not self.active_zone:
			if logging: self.save_to_log('image')
			self.array = function(self.array)
			self.update_function()
			if self.widg.pixel.np.array_equal(ancient, self.array) and logging:
				self.log.pop(-1)
		else:
			if logging: self.save_to_log('image')
			zone = self.Zone.get_zone()
			zone = function(zone)
			self.array = self.Zone.apply_zone(zone, array=self.array)
			self.update_function()
			if self.widg.pixel.np.array_equal(ancient, self.array) and logging:
				self.log.pop(-1)
		ancient = None
		del ancient

	def get_log_value(self, info, table=None):
		# get the right information from a given log
		if info == 'image':
			return self.array
		elif info == 'zone erasion':
			return None
		elif info == 'zone creation':
			return self.Zone.clone()
		elif info == 'zone motion':
			return self.Zone.nodes[:]
		else:
			raise NameError('"{}" is not a valid log info name'.format(info))

	def get_new_log(self, log):
		# change the logs info (e.g. erase -> create, etc.)
		info, _ = log
		if info.split()[0] == 'zone':
			arg = info.split()[1]
			arg = 'creation' if arg == 'erasion' else 'erasion' if arg != 'motion' else 'motion'
			#value = None if arg == 'creation' else self.Zone if arg != 'motion' else self.Zone.clone_nodes()
			return ('zone ' + arg, log[1])
		#elif ...
		# nothing to change (e.g. for 'image')
		return log

	def undo(self):
		if len(self.log):
			print('undo', len(self.log), self.log[-1][0], type(self.log[-1][1]))

			# handle multiple at the root is more simple than somewhere else
			if self.log[-1][0] == 'multiple':
				self.redo_log.append((self.log[-1][0], [self.get_new_log(sub_log) for sub_log in self.log[-1][1]]))
				for sub_log in self.log[-1][1]:
					# do everything manually here
					self.handle_log(sub_log)
				self.log.pop(-1)
				self.update_function()
				return

			# append current image to redo_log
			info = self.log[-1][0]
			self.redo_log.append(self.get_new_log((info, self.get_log_value(info))))

			# get the last registered image in log
			self.handle_log(self.log[-1])
			# delete the current image from log
			self.log.pop(-1)
		self.update_function()

	def redo(self):
		if len(self.redo_log):
			print('redo', len(self.redo_log), self.log[-1][0], type(self.redo_log[-1][1]))

			# handle multiple at the root is more simple than somewhere else
			if self.redo_log[-1][0] == 'multiple':
				self.log.append((self.redo_log[-1][0], [self.get_new_log(sub_log) for sub_log in self.redo_log[-1][1]]))
				for sub_log in self.redo_log[-1][1]:
					# do everything manually here
					self.handle_log(sub_log)
				self.redo_log.pop(-1)
				self.update_function()
				return

			# same principle as in undo, but log -> redo, redo -> log
			info = self.redo_log[-1][0]
			self.log.append(self.get_new_log((info, self.get_log_value(info))))

			self.handle_log(self.redo_log[-1])
			self.redo_log.pop(-1)
		self.update_function()

	def handle_log(self, log_info):
		# Handles the event described in the log
		info, value = log_info
		if info == 'image':
			self.array = value
		elif info == 'zone creation':
			print('erasing created zone with value {}'.format(value))
			self.active_zone = False
			self.Zone.erase()
			self.Zone = None
		elif info == 'zone erasion':
			print('creating erased zone with value {}'.format(value))
			self.widg.GUIf.ui.sz.__Zone__ = self.Zone
			self.widg.GUIf.ui.sz.__current__ = True
			self.active_zone = True
			self.Zone = value.clone()
			self.Zone.init_motion()
		elif info == 'zone motion':
			print('setting zone position to', value[0].position)
			self.Zone.nodes = value[:]
		else:
			raise NameError('"{}" is not a valid log info name'.format(info))

	def clear_log(self):
		self.log.clear()
		self.redo_log.clear()

	def check_log(self, MAX_LOG_LENGTH):
		if len(self.log) + len(self.redo_log) > MAX_LOG_LENGTH:
			if len(self.log): self.log.pop(0)
			if len(self.redo_log): self.redo_log.pop(0)

	def to_last_opened(self, clear_redo=False):
		self.save_to_log('image')
		self.mini_change(self.last_opened)
		if clear_redo:
			self.redo_log.clear()

	def to_default(self):

		self.save_to_log('image')

		self.array = self.default
		self.array_backup = self.default.copy()

		self.widg.IF_image_size_label['text'] = 'no size'
		self.widg.IF_image_location_label['text'] = 'none'
		self.widg.IF_opened_at_label['text'] = 'opened at ---'

		self.update_function()
