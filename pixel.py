# look at images with pygame
from PIL import Image
import imageio, cv2, screeninfo, os, shutil, datetime
import scipy.misc as scm
import numpy as np

# own side-modules
from c_functions import replace_color_in_image_by_image

# ---- variables -----
rgb_color = {'black': (0, 0, 0), 'red': (190, 0, 0), 'light_red': (255, 0, 0), 'green': (34, 177, 76), 'light_green': (0, 255, 0), 'yellow': (190, 190, 0), 'light_yellow': (235, 235, 0), 'blue': (0, 0, 230), 'light_blue': (0, 160, 255), 'grey': (190, 190, 190), 'light_grey': (221, 221, 221), 'pink': (190, 0, 190), 'light_pink': (240, 0, 240), 'white': (255, 255, 255), 'very_light_grey': (255, 255, 255), 'dark_grey': (120, 120, 120), 'dark_red': (110, 0, 0), 'very_light_red': (255, 60, 60), 'dark_green': (10, 110, 20), 'dark_yellow': (110, 110, 0), 'very_light_yellow': (255, 255, 45), 'dark_pink': (120, 0, 120), 'very_light_pink': (255, 20, 255), 'very_light_green': (100, 255, 100), 'very_light_blue': (0, 255, 255), 'dark_blue': (0, 0, 180)}
bgr_color = dict([(name, value[::-1]) for name, value in list(rgb_color.items())])

# screen
monitor = screeninfo.get_monitors()[0]
destroy_window_after_shown = True

# ----- Show & Destroy images -----
# lambda functions
destroy = lambda : cv2.destroyAllWindows()
webcam_shot = lambda : cv2.VideoCapture(0).read()
load = lambda path : imageio.imread(open(path, 'rb'))

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
        img = resize(img, (int(img.shape[1]*ratio), int(img.shape[0]*ratio)))
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
def brightness(img, ratio=1.1):

    # brighten function
    brighten = lambda pixel, ratio : np.array([v*ratio if v*ratio <= 255 else 255 for v in pixel])

    # go trhough all pixel (idk why it doesn't work in a one-line for-loop)
    for x,column in enumerate(img):
        for y,pixel in enumerate(column):
            img[x][y] = brighten(pixel,ratio)#np.array([v*ratio if v*ratio <= 255 else 255 for v in pixel])

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
def detect_object(img, scaleFactor=1.1, minNeighbors=5, minSize=(30,30), rectangle_color=(0,255,0), cascade_file_path='/root/git_clones/FaceDetect/haarcascade_frontalface_default.xml'):

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
def webcam_detect_object(return_last_frame=False, scaleFactor=1.1, minNeighbors=5, minSize=(30,30), rectangle_color=(0,255,0), cascade_file_path='/root/git_clones/FaceDetect/haarcascade_frontalface_default.xml'):

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


class Video:

    def __init__(self, source):
        '''
         --- docstring for "Video" ---

        This class' purpose is video editing.
        The main object will be a video file (self.source),
        but you will interract with a copy of it,
        which is located in the self.output.
        To clean this tmp file, you can use the "clean" method.

        Those are the available methods:
         - clean: delete the temp file of your video editing
         - update: save the changes that you have made to your source file
         - show_tmp: visualize the 'working-on'-video
         - show: visualize the video
         - loop_show: visualize the video in a while loop, except you press "q"
         - resize: resize the video by a given size
         - edit: give a function which will edit every frame of the video
         - get_frame_index_by_time: get the frame-index to cut by index
         - cut_by_frame_index: cut the video by frame-index
         - get_frame: get the n frame from the video

        '''

        # source & output files
        self.source = source
        self.output = os.path.join(os.getcwd(), 'tmp_video_file_{}.avi'.format(str(datetime.datetime.now()).replace(' ', '_')[:-1].split('.')[0]))

        # Video Capture
        self.capture = lambda : cv2.VideoCapture(self.source)

        # info
        self.get_resolution = lambda : (int(self.capture().get(cv2.CAP_PROP_FRAME_HEIGHT)), int(self.capture().get(cv2.CAP_PROP_FRAME_WIDTH)))
        self.get_total_frames = lambda : self.capture().get(cv2.CAP_PROP_FRAME_COUNT)
        self.get_fourcc = lambda : self.capture().get(cv2.CAP_PROP_FOURCC)

    def clean(self):
        # remove the temp file
        try: os.remove(self.output)
        except FileNotFoundError: print('Already clean')

    def update(self):

        # overwrite the tmp output file (if it exists)
        # to the source file
        if os.path.isfile(self.output):
            shutil.copy(self.output, self.source)
            os.rename(self.output, self.source)
        else:
            raise ValueError('There is no tmp file yet! You must first edit the video to be able save it')

    # show the tmp-video. It stops by pressing 'q'
    def show_tmp(self):

        cap = cv2.VideoCapture(self.output)

        while cap.isOpened():

            ret, frame = cap.read()
            if ret:
                cv2.imshow('main', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    cap.release()
                    cv2.destroyAllWindows()
                    return True

            else:
                cap.release()
                if destroy_window_after_shown: cv2.destroyAllWindows()
                return False

    # show the video. It stops by pressing 'q'
    def show(self):

        cap = self.capture()

        while cap.isOpened():

            ret, frame = cap.read()
            if ret:
                cv2.imshow('main', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    cap.release()
                    cv2.destroyAllWindows()
                    return True

            else:
                cap.release()
                if destroy_window_after_shown: cv2.destroyAllWindows()
                return False

    def loop_show(self):

        while True:
            if self.show():
                cap = self.capture()
                while cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        cv2.imshow('main', frame)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            cap.release()
                            return True
                    else:
                        cap.release()
                        return False

    def resize(self, size, verbose=1, step=50): # DOESNT WORK YET
        # use edit to resize the video
        self.edit(lambda frame: cv2.resize(frame, size), verbose, step)

    def edit(self, editation, verbose=0, step=50):
        # the editation sould be a function (lambda is a good way),
        # which has already all the wanted arguments in it

        # capture
        cap = self.capture()
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        # outfile
        out = cv2.VideoWriter(self.output, int(cap.get(cv2.CAP_PROP_FOURCC)), cap.get(cv2.CAP_PROP_FPS), (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

        frame_counter = 0
        # while still in the video
        while cap.isOpened():

            if verbose == 1 and frame_counter % step == 0:
                print('Finished {} frames from total {}'.format(frame_counter, length))
            frame_counter += 1

            # get next frame
            ret, frame = cap.read()

            if ret:

                # flip the frame
                frame = editation(frame)

                # write the flipped frame
                out.write(frame)

            else:
                break

        cap.release()

    # get the frame index by a given second from the video
    def get_frame_index_by_time(self, from_second, to_second):

        FPS = self.capture().get(cv2.CAP_PROP_FPS)
        return from_second * FPS, to_second * FPS

    def cut_by_frame_index(self, from_index, to_index):

        # capture
        cap = self.capture()
        # outfile
        out = cv2.VideoWriter(self.output, int(cap.get(cv2.CAP_PROP_FOURCC)), cap.get(cv2.CAP_PROP_FPS), (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

        if from_index < 0:
            from_index += cap.get(cv2.CAP_PROP_FRAME_COUNT) # it's a negative number, so it'll decrease from the max
        if to_index < 0:
            to_index += cap.get(cv2.CAP_PROP_FRAME_COUNT)

        frame_counter = 0
        # while still in the video
        while cap.isOpened():

            # get next frame
            ret, frame = cap.read()

            if ret and frame_counter <= to_index:

                if from_index <= frame_counter:

                    # write the flipped frame
                    out.write(frame)

            else:
                break

            frame_counter += 1

        cap.release()

    # get the n frame of the video
    def get_frame(self, frame_index):

        # capture
        cap = self.capture()

        if frame_index < 0:
            frame_index += cap.get(cv2.CAP_PROP_FRAME_COUNT)

        # make sure the frame_index is in the frame-range of the video
        assert frame_index < cap.get(cv2.CAP_PROP_FRAME_COUNT)

        frame_counter = 0
        # while still in the video
        while cap.isOpened():

            # get next frame
            ret, frame = cap.read()

            if ret and frame_counter == frame_index:

                    return frame

            frame_counter += 1

        raise RuntimeError('An Error has occured: probably an early closing of the Video')
