import tkinter as tk
from tkinter.messagebox import showerror

class CustomTkWidget:

	def __init__(self, frame, info, function, popup_onerror=True, TkWidget=tk.Button, **kwargs):

		self.frame = frame
		self.info = info
		self.function = function

		self.popup_onerror = popup_onerror
		self.kwargs = kwargs

		self.TkWidget = TkWidget

		self.widget = self.TkWidget(self.frame, command=self.call, **kwargs)

	def call(self):
		# try:
		self.function(self.info)
		# except TypeError:
			# if self.popup_onerror:
				# showerror('Erreur', 'L\'emplacement demandé semble être vide dans le tableur Excel. (Il est conseillé de redémarrer le programme pour éviter divers bugs)')

	def destroy(self):
		self.widget.destroy()

