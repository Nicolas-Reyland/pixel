# Pixel Module - Video Editing
from PIL import Image
import cv2, os, shutil, datetime
import numpy as np

class Video:

    def __init__(self, source):
        '''
         --- Video Class ---

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
        # fourcc
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        # Video Capture
        self.capture = lambda : cv2.VideoCapture(self.source)

        # info
        self.get_resolution = lambda : (int(self.capture().get(cv2.CAP_PROP_FRAME_HEIGHT)), int(self.capture().get(cv2.CAP_PROP_FRAME_WIDTH)))
        self.get_total_frames = lambda : int(self.capture().get(cv2.CAP_PROP_FRAME_COUNT))
        self.get_fourcc = lambda : self.capture().get(cv2.CAP_PROP_FOURCC)
        self.get_fps = lambda : self.capture().get(cv2.CAP_PROP_FPS)

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

    def resize(self, size, verbose=1, stdout_step=50): # DOESNT WORK YET
        # use edit to resize the video
        self.edit(lambda frame: cv2.resize(frame, size), verbose, stdout_step)

    def edit(self, editation, verbose=0, stdout_step=50):
        # the editation sould be a function (lambda is a good way),
        # which has already all the wanted arguments in it

        # capture
        cap = self.capture()
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        # outfile
        #fourcc = cv2.VideoWriter_fourcc(*'mp4v') # int(cap.get(cv2.CAP_PROP_FOURCC))
        out = cv2.VideoWriter(self.output, self.fourcc, cap.get(cv2.CAP_PROP_FPS), (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

        frame_counter = 0
        # while still in the video
        while cap.isOpened():

            if verbose == 1 and frame_counter % stdout_step == 0:
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
        out = cv2.VideoWriter(self.output, self.fourcc, cap.get(cv2.CAP_PROP_FPS), (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

        if from_index < 0:
            from_index += cap.get(cv2.CAP_PROP_FRAME_COUNT) # it's a negative number, so it'll decrease from the max
        if to_index < 0:
            to_index += cap.get(cv2.CAP_PROP_FRAME_COUNT)

        frame_counter = 1
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


#
