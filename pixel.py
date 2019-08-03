# look at images with pygame
from PIL import Image, ImageEnhance
import imageio, cv2, screeninfo
import scipy.misc as scm
import numpy as np

# own side-modules
from c_functions import replace_color_in_image_by_image
import video

# ---- variables -----
# my own shortcut-variables
Hayao = '/root/Images/Hayao Miyazaki.jpg'
hokusai = '/root/Images/Tsunami_by_hokusai_19th_century.jpg'
source = video.Video('/root/Vidéos/intro bob lennon.avi')
import os
clear = lambda : os.system('clear')

hay = lambda : cv2.cvtColor(imageio.imread(open(Hayao, 'rb')), cv2.COLOR_BGR2RGB)
hoku = lambda : cv2.cvtColor(np.array(Image.fromarray(imageio.imread(open(hokusai, 'rb'))).resize(hay().shape[:-1][::-1])), cv2.COLOR_BGR2RGB)


# the remaining
rgb_color = {'black': (0, 0, 0), 'red': (190, 0, 0), 'light_red': (255, 0, 0), 'green': (34, 177, 76), 'light_green': (0, 255, 0), 'yellow': (190, 190, 0), 'light_yellow': (235, 235, 0), 'blue': (0, 0, 230), 'light_blue': (0, 160, 255), 'grey': (190, 190, 190), 'light_grey': (221, 221, 221), 'pink': (190, 0, 190), 'light_pink': (240, 0, 240), 'white': (255, 255, 255), 'very_light_grey': (255, 255, 255), 'dark_grey': (120, 120, 120), 'dark_red': (110, 0, 0), 'very_light_red': (255, 60, 60), 'dark_green': (10, 110, 20), 'dark_yellow': (110, 110, 0), 'very_light_yellow': (255, 255, 45), 'dark_pink': (120, 0, 120), 'very_light_pink': (255, 20, 255), 'very_light_green': (100, 255, 100), 'very_light_blue': (0, 255, 255), 'dark_blue': (0, 0, 180)}
bgr_color = dict([(name, value[::-1]) for name, value in list(rgb_color.items())])
from ascii_enc_dec import enc as encode_to_base
rgb_to_hex = lambda rgb: '#' + ''.join([x + (2 - len(x))*'0' for x in list(map(lambda r: encode_to_base(r,16),rgb))])

# screen
try: monitor = screeninfo.get_monitors()[0]
except IndexError: pass
destroy_window_after_shown = True
video.destroy_window_after_shown = destroy_window_after_shown

# ----- Show & Destroy images -----
# lambda functions
destroy = lambda : cv2.destroyAllWindows()
webcam_shot = lambda : cv2.VideoCapture(0).read()
load = lambda path : imageio.imread(open(path, 'rb'))
save = lambda array,path: Image.fromarray(array, mode='RGB').save(path, format='BMP')

# show
def showimage(img, ratio=1, size=('default', 'default'), auto_scale=False, change_color_channel=False, color_channel_function=cv2.COLOR_BGR2RGB, return_img=False, name='main'):
    assert ratio > 0
    # to know if the image-size has been customized
    modify_size = any(x != 'default' for x in size)

    # you cannot have a ratio + a custom image-size
    if modify_size and ratio != 1:
        ValueError('Ratio can not be {} when size is not "default"')

    # if the given img is a string, assume it's an image file
    if type(img) == str:
        img = imageio.imread(open(img,'rb'))

    # autoscale if no specific ratio or size has been given
    img_width, img_height = img.shape[1], img.shape[0] + 95
    if ratio == 1 and not modify_size and auto_scale:
        global monitor
        if img_width > monitor.width:
            ratio = monitor.width / img_width
            print('resize width')
        if img_height > monitor.height:
            ratio = monitor.height / img_height if ratio > monitor.height / img_height else ratio
            print('resize height')

    # change image by ratio
    if ratio != 1:
        img = resize(img, (int(img.shape[0]*ratio), int(img.shape[1]*ratio)))
    # change image by given size
    elif modify_size:

        # change the 'default' in size
        for i,x in enumerate(size):
            if x == 'default':
                size[i] = img.shape[i]

        # resize the image
        img = resize(img, (size[0], size[1]))

    # change to choosen color channel
    if change_color_channel:
        img = cv2.cvtColor(img, color_channel_function)

    # show image
    cv2.imshow(name, img)
    cv2.waitKey(0)

    if destroy_window_after_shown: destroy()

    if return_img: return img

# ----- Easy -----
# pixel match function
pixel_match = lambda target, pixel, tolerance : all([abs(pixel[i] - target[i]) <= tolerance for i in range(len(pixel))])

# grayscale an image
grayscale = lambda array: cv2.cvtColor(array, cv2.COLOR_BGR2GRAY)

# List of changes, applied one afther the other
def easy_change(img, function_list, show_progress=False):
    for function in function_list:
        img = function(img)
        if show_progress: showimage(img)
    return img

resize = lambda img, size: np.array(Image.fromarray(img).resize(size[::-1]))

# resize an image to the size of an other one
def adapt_size(img, target_img):

    if not hasattr(target_img, 'shape'):
        desired = np.array(target_img)
    if not hasattr(img, 'shape'):
        desired = np.array(img)

    if img.shape != target_img.shape:
        img = resize(img, (target_img.shape[0], target_img.shape[1]))

    return img

# brightness
def brightness(img, value):
    img = np.int16(img)
    img = np.add(img, value)
    img = img.clip(0,255)
    img = np.uint8(img)
    return img

# saturation
def saturation(img, value):

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    if value > 0: v = np.where(v <= 255 - value, v + value, 255)
    else: v = np.where(v >= abs(value), v - abs(value), 0)

    final_hsv = cv2.merge((h,s,v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)

    return img

# sharpness
def sharpen(img, ratio=1):
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    kernel *= ratio
    img = cv2.filter2D(img, -1, kernel)
    return img


# half vertical-, horizontal-partial (the best is u test them, coz it's pretty weird)
horizontal_partial = lambda img: np.array([column if x % 2 else column[::-1] for x,column in enumerate(img)])
vertical_partial = lambda img : np.array(list(zip(*[row if x % 2 else row[::-1] for x,row in enumerate(list(zip(*img)))])))

# diaporama
def diaporama(x):
    if type(x) == str:
        for f in os.listdir(x):
            try: showimage(os.path.join(x, f), auto_scale=True)
            except ValueError: pass
    elif type(x) == np.ndarray or type(x) == list:
        for i in x:
            showimage(i, auto_scale=True)
    else:
        raise NotImplementError('The {} type is not supported'.format(type(x)))


# ----- Object Detection -----
# Object Detection
def detect_object(img, scaleFactor=1.1, minNeighbors=5, minSize=(30,30), rectangle_color=(0,255,0), cascade_file_path='/home/valar/git_clones/FaceDetect/haarcascade_frontalface_default.xml'):

    # define Cascade-Classifier
    faceCascade = cv2.CascadeClassifier(cascade_file_path)

    # gray-scale the image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # detect faces in the image
    faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=scaleFactor,
            minNeighbors=minNeighbors,
            minSize=minSize,
            flags=cv2.CASCADE_SCALE_IMAGE
    )

    # draw rectangles
    for (x,y,w,h) in faces:
        cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)

    return img

# Webcam Object Detection
def webcam_detect_object(return_last_frame=False, scaleFactor=1.1, minNeighbors=5, minSize=(30,30), rectangle_color=(0,255,0), cascade_file_path='/home/valar/git_clones/FaceDetect/haarcascade_frontalface_default.xml'):

    # define Cascade-Classifier
    faceCascade = cv2.CascadeClassifier(cascade_file_path)

    # define video_capture
    video_capture = cv2.VideoCapture(0)

    # main loop
    while True:
        # Capture frame by frame
        ret, frame = video_capture.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30,30),
                flags=cv2.CASCADE_SCALE_IMAGE
                )

        # Draw a rectangle around the faces
        for (x,y,w,h) in faces:
            cv2.rectangle(frame, (x,y), (x+w,y+h), rectangle_color)

        # Display the resulting frame
        cv2.imshow('Video', frame)

        if cv2.waitKey(1) in [27, 113]:
            break

    # When everything is done, release the capture
    video_capture.release()

    if destroy_window_after_shown: destroy()

    if return_last_frame: return frame
