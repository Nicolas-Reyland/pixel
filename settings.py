# Settings
import tkinter as tk
from tkinter.messagebox import showwarning, askokcancel
from tkinter import filedialog
from tkinter.ttk import Combobox
from tkinter import filedialog
from copy import copy
import tkcolorpicker
import json, os


settings = {}
settings_backup = {}
toplevel = None

def create_toplevel():
    # settings toplevel
    toplevel = tk.Toplevel()
    toplevel.title('Settings')
    toplevel.attributes('-topmost', 'true')
    toplevel.resizable(False, False)
    toplevel.protocol('WM_DELETE_WINDOW', toplevel.withdraw)
    toplevel.withdraw()
    return toplevel

# widgets
widgets = {}

def init():
    global toplevel, settings, widgets
    # toplevel
    toplevel = create_toplevel()
    # settings
    if not os.path.isfile('data/settings.json'):
        settings = create_settings()
    else:
        settings = read_settings()
    # widgets
    widgets = fill_toplevel(toplevel, settings)

def read_settings():
    with open('data/settings.json', 'rb') as file:
        settings = json.load(file)
    return settings

def create_settings():
    with open('data/settings.json', 'w') as file:
        # General
        settings['default image'] = 'auto'
        settings['use custom default image'] = False
        settings['use keyboard shortcuts'] = True
        settings['fullscreen'] = False
        settings['base path'] = ''
        # webcam
        settings['cascade file path'] = ''
        settings['allow webcam'] = True

        # Zone
        settings['intern node color'] = (200,200,200)
        settings['extern node color'] = (10,10,10)
        settings['line color'] = (10,10,10)
        settings['line thickness'] = 1
        settings['smoothing algorithm'] = 'Chaikin' # ?PEAK?, ?Berkin?
        settings['smooth var'] = 4 # make available only when needed

        # rciibi
        settings['rciibi color'] = (255,255,255)
        settings['rciibi image'] = None
        settings['rciibi tolerance'] = 10

        # RAM, Memory usage
        settings['max RAM usage'] = 95 # %
        settings['max Memory usage'] = 1000 # Mb
        settings['close program when max RAM exceeds'] = True
        settings['close program when max Memory exceeds'] = False
        settings['max log length'] = 30
        settings['clear image when freeing RAM'] = True

        json.dump(settings, file)

    return settings

def fill_toplevel(toplevel, settings):

    title_font = 'Times 15'
    widgets = {}

    # - General -
    general_label = tk.Label(toplevel, text='General', font=title_font)
    general_label.grid(row=0,column=0,columnspan=4)

    # default image & use custom default image
    df_bg_image_var = tk.BooleanVar()
    df_bg_image_var.set(settings['use custom default image'])
    df_bg_image_check = tk.Checkbutton(toplevel, text=' use custom default image', variable=df_bg_image_var, command=lambda : change_setting('use custom default image'))
    df_bg_image_check.grid(row=1,column=0,columnspan=2)
    df_bg_image_button = tk.Button(toplevel, text='Choose custom image', command=lambda : change_setting('default image'))
    df_bg_image_button.grid(row=2,column=0,columnspan=2)
    widgets['use custom default image var'] = df_bg_image_var

    # use keyboard shortcuts
    use_kb_sc_var = tk.BooleanVar()
    use_kb_sc_var.set(settings['use keyboard shortcuts'])
    use_kb_sc_check = tk.Checkbutton(toplevel, text=' use keyboard shortcuts', variable=use_kb_sc_var, command=lambda : change_setting('use keyboard shortcuts'))
    use_kb_sc_check.grid(row=3,column=0,columnspan=2)
    widgets['use keyboard shortcuts var'] = use_kb_sc_var

    # fullscreen
    fullscreen_var = tk.BooleanVar()
    fullscreen_var.set(settings['fullscreen'])
    fullscreen_check = tk.Checkbutton(toplevel, text=' fullscreen', variable=fullscreen_var, command=lambda : change_setting('fullscreen'))
    fullscreen_check.grid(row=4,column=0,columnspan=2)
    widgets['fullscreen var'] = fullscreen_var

    # base path
    base_path_button = tk.Button(toplevel, text='Choose base path', command=lambda : change_setting('base path'))
    base_path_button.grid(row=1,column=2,columnspan=2)

    # cascade file path
    cascade_file_path_button = tk.Button(toplevel, text='Cascade file path', command=lambda : change_setting('cascade file path'))
    cascade_file_path_button.grid(row=2,column=2,columnspan=2)

    # allow webcam
    allow_webcam_var = tk.BooleanVar()
    allow_webcam_var.set(settings['allow webcam'])
    allow_webcam_check = tk.Checkbutton(toplevel, text=' allow webcam', variable=allow_webcam_var, command=lambda : change_setting('allow webcam'))
    allow_webcam_check.grid(row=3,column=2,columnspan=2)
    widgets['allow webcam var'] = allow_webcam_var


    # - Zone -
    zone_label = tk.Label(toplevel, text='Zone', font=title_font)
    zone_label.grid(row=5,column=0,columnspan=4)

    # node colors
    intern_node_color_button = tk.Button(toplevel, text='intern node color', command=lambda : change_setting('intern node color'))
    intern_node_color_button.grid(row=6,column=0,columnspan=2)
    extern_node_color_button = tk.Button(toplevel, text='extern node color', command=lambda : change_setting('extern node color'))
    extern_node_color_button.grid(row=7,column=0,columnspan=2)

    # line color, thickness
    line_color_button = tk.Button(toplevel, text='line color', command=lambda : change_setting('line color'))
    line_color_button.grid(row=6,column=2,columnspan=2)
    line_thickness_scale = tk.Scale(toplevel, from_=1, to=5, label='line thickness', orient=tk.HORIZONTAL, command=lambda x: change_setting('line thickness'))
    line_thickness_scale.grid(row=7,column=2,columnspan=2,sticky='ew')
    line_thickness_scale.set(settings['line thickness'])
    widgets['line thickness scale'] = line_thickness_scale

    # smoothing algorithm
    smooth_alg_combo = Combobox(toplevel, values=['Chaikin', 'PAEK', 'Bezier'])
    # PAEK = Polygonial Approximation with Exponential Kernel
    smooth_alg_combo.set(settings['smoothing algorithm'])
    smooth_alg_combo.grid(row=8,column=0,columnspan=2)
    widgets['smoothing algorithm combo'] = smooth_alg_combo

    # smoothing variable
    smooth_n_scale = tk.Scale(toplevel, from_=3, to=10, label='smoothing variable', orient=tk.HORIZONTAL, command=lambda x: change_setting('smooth var'))
    smooth_n_scale.grid(row=8,column=2,columnspan=2,sticky='ew')
    smooth_n_scale.set(settings['smooth var'])
    widgets['smooth var scale'] = smooth_n_scale

    # - rciibi -
    rciibi_label = tk.Label(toplevel, text='RCiIbI', font=title_font)
    rciibi_label.grid(row=9,column=0,columnspan=4)

    # rciibi color
    rciibi_color = tk.Button(toplevel, text='default rciibi color', command=lambda : change_setting('rciibi color'))
    rciibi_color.grid(row=10,column=0,columnspan=2)

    # rciibi image
    rciibi_image = tk.Button(toplevel, text='default rciibi image', command=lambda : change_setting('rciibi image'))
    rciibi_image.grid(row=10,column=2,columnspan=2)

    # tolerance
    tolerance_scale = tk.Scale(toplevel, from_=1, to=255, label='default tolerance', orient=tk.HORIZONTAL, command=lambda x: change_setting('rciibi tolerance'))
    tolerance_scale.set(settings['rciibi tolerance'])
    tolerance_scale.grid(row=11,column=0,columnspan=4,sticky='ew')
    widgets['rciibi tolerance scale'] = tolerance_scale


    # - RAM, Memory usage -
    ram_mem_usage_label = tk.Label(toplevel, text='RAM & Memory Usage', font=title_font)
    ram_mem_usage_label.grid(row=12,column=0,columnspan=4)

    # max RAM
    max_RAM_scale = tk.Scale(toplevel, from_=10, to=100, label='max RAM usage (%)', orient=tk.HORIZONTAL, command=lambda x: change_setting('max RAM usage'))
    max_RAM_scale.set(settings['max RAM usage'])
    max_RAM_scale.grid(row=13,column=0,columnspan=2,sticky='ew')
    widgets['max RAM usage scale'] = max_RAM_scale

    # max Memmory
    max_Memory_label = tk.Label(toplevel, text='max Memory usage (Mb): ')
    max_Memory_label.grid(row=14,column=0)
    max_Memory_Entry = tk.Entry(toplevel)
    max_Memory_Entry.grid(row=14,column=1)
    max_Memory_Entry.insert(tk.END, settings['max Memory usage'])
    widgets['max Memory usage entry'] = max_Memory_Entry

    # close program at max RAM excess
    close_at_max_RAM_var = tk.BooleanVar()
    close_at_max_RAM_var.set(settings['close program when max RAM exceeds'])
    close_at_max_RAM_check = tk.Checkbutton(toplevel, text='close at RAM excess', variable=close_at_max_RAM_var, command=lambda : change_setting('close program when max RAM exceeds'))
    close_at_max_RAM_check.grid(row=13,column=2,columnspan=2)
    widgets['close program when max RAM exceeds var'] = close_at_max_RAM_var

    # close program at max Memory excess
    close_at_max_Memory_var = tk.BooleanVar()
    close_at_max_Memory_var.set(settings['close program when max Memory exceeds'])
    close_at_max_Memory_check = tk.Checkbutton(toplevel, text='close at Memory excess', variable=close_at_max_Memory_var, command=lambda : change_setting('close program when max Memory exceeds'))
    close_at_max_Memory_check.grid(row=14,column=2,columnspan=2)
    widgets['close program when max Memor exceeds var'] = close_at_max_Memory_var

    # max log length
    max_log_length_scale = tk.Scale(toplevel, from_=0, to=100, label='max log length', orient=tk.HORIZONTAL, command=lambda x: change_setting('max log length'))
    max_log_length_scale.set(settings['max log length'])
    max_log_length_scale.grid(row=15,column=0,columnspan=2,sticky='ew')
    widgets['max log length scale'] = max_log_length_scale

    # clear image at RAM freeing
    clear_image_at_RAM_freeing_var = tk.BooleanVar()
    clear_image_at_RAM_freeing_var.set(settings['clear image when freeing RAM'])
    clear_image_at_RAM_freeing_check = tk.Checkbutton(toplevel, text='clear image when freeing RAM', variable=clear_image_at_RAM_freeing_var, command=lambda : change_setting('clear image when freeing RAM'))
    clear_image_at_RAM_freeing_check.grid(row=15,column=2,columnspan=2)
    widgets['clear image when freeing RAM var'] = clear_image_at_RAM_freeing_var


    # - Default, Ok, Cancel -
    separation_label = tk.Label(toplevel, text='-' * 100)
    separation_label.grid(row=16,column=0,columnspan=4)

    # default
    default_button = tk.Button(toplevel, text='Default', command=lambda : default_settings(toplevel))
    default_button.grid(row=17,column=0)

    # cancel
    cancel_button = tk.Button(toplevel, text='Cancel', command=cancel_settings)
    cancel_button.grid(row=17,column=1,columnspan=2)

    # OK
    ok_button = tk.Button(toplevel, text='OK', command=confirm_settings)
    ok_button.grid(row=17,column=3)

    return widgets

def change_setting(key):
    global settings, widgets
    print(f'changing {key}')

    if key == 'use custom default image':
        settings['use custom default image'] = widgets['use custom default image var'].get()
    elif key == 'default image':
        if settings['use custom default image']:
            settings['default image'] = askfile(settings['default image'],
                                        title='Choose custom default image',
                                        initialdir=settings['base path'],
                                        #filetypes=[('images', '*')]
                                        )
        else:
            showwarning('Warning', 'You have chosen not to use a custom image as default image')
    elif key == 'use keyboard shortcuts':
        settings[key] = widgets[f'{key} var'].get()
    elif key == 'fullscreen':
        settings[key] = widgets[f'{key} var'].get()
    elif key == 'base path':
        settings[key] = askfolder(settings[key],
                                title='Choose base path',
                                initialdir=settings['base path']
                                )
    elif key == 'cascade file path':
        settings[key] = askfile(settings[key],
                                title=settings['base path'],
                                initialdir=settings['base path'],
                                filetypes=[('cascade', '*.xml')])
    elif key == 'allow webcam':
        settings[key] = widgets[f'{key} var'].get()
    elif key == 'intern node color':
        color = tkcolorpicker.askcolor(settings[key])
        if color[0]: settings[key] = color[0]
    elif key == 'extern node color':
        color = tkcolorpicker.askcolor(settings[key])
        if color[0]: settings[key] = color[0]
    elif key == 'line color':
        color = tkcolorpicker.askcolor(settings[key])
        if color[0]: settings[key] = color[0]
    elif key == 'line thickness':
        settings[key] = widgets[f'{key} scale'].get()
    elif key == 'smoothing algorithm': # not supported yet
        settings[key] = widgets[f'{key} combo'].get()
    elif key == 'smooth var':
        settings[key] = widgets[f'{key} scale'].get()
    elif key == 'rciibi color':
        color = tkcolorpicker.askcolor(settings[key])
        if color[0]: settings[key] = color[0]
    elif key == 'rciibi image':
        settings[key] = askfile(settings[key],
                        title='Choose default rciibi image',
                        initialdir=settings['base path'])
    elif key == 'rciibi tolerance':
        settings[key] = widgets[f'{key} scale'].get()
    elif key == 'max RAM usage':
        settings[key] = widgets[f'{key} scale'].get()
    elif key == 'max Memmory usage':
        settings[key] = int(widgets['max Memory usage entry'].get())
    elif key == 'close program when max RAM exceeds':
        settings[key] = widgets[f'{key} var'].get()
    elif key == 'close program when max Memory exceeds':
        settings[key] = widgets[f'{key} var'].get()
    elif key == 'max log length':
        settings[key] = widgets[f'{key} scale'].get()
    elif key == 'clear image when freeing RAM':
        settings[key] = widgets[f'{key} var'].get()

    else:
        raise NameError(f'key "{key}" is not recognized')

def default_settings(toplevel):
    global settings, settings_backup
    if askokcancel('Default Settings', 'Set all settings to default ?'):
        os.remove('data/settings.json')
        settings = create_settings()
        settings_backup = copy(settings)
        toplevel.withdraw()
        print('settings to default')



def askfile(default_value, **kwargs):
    filename = filedialog.askopenfilename(**kwargs)
    return filename if filename else default_value

def askfolder(default_value, **kwargs):
    foldername = filedialog.askdirectory(**kwargs)
    return foldername if foldername else default_value

def save_settings(settings, settings_backup, widgets):

    if settings['use keyboard shortcuts']:
        widg.GUIf.ui.keyboard_shortcuts_binding.bind()
    else:
        widg.GUIf.ui.keyboard_shortcuts_binding.unbind()

    if settings['fullscreen']:
        widg.root.update()
        widg.root.geometry('{0}x{1}+{2}+{3}'.format(widg.root.winfo_screenwidth(), widg.root.winfo_screenheight(), 0, 0))
        widg.root.attributes('-fullscreen', True)
    elif settings_backup['fullscreen']:
        widg.root.update()
        width, height = widg.base_root_dimensions
        x, y = widg.base_root_coordinates
        widg.root.geometry('{0}x{1}+{2}+{3}'.format(width, height, x, y))
        widg.root.attributes('-fullscreen', False)

    return settings

def dump_settings(settings):
    with open('data/settings.json', 'w') as file:
        json.dump(settings, file)

def confirm_settings():
    global toplevel, settings, settings_backup, widgets
    toplevel.withdraw()
    settings = save_settings(settings, settings_backup, widgets)
    widgets = fill_toplevel(toplevel, settings)
    dump_settings(settings)

def cancel_settings():
    global toplevel, settings, settings_backup, widgets
    toplevel.withdraw()
    settings = copy(settings_backup)
    widgets = fill_toplevel(toplevel, settings)

def show_toplevel():
    global toplevel, settings, settings_backup, widgets
    # destroy all children of the parent
    for child in toplevel.winfo_children():
        child.destroy()
    # fill toplevel
    widgets = fill_toplevel(toplevel, settings)
    settings_backup = copy(settings)
    toplevel.deiconify()

