import cv2
import time
import threading

def get_video_capture(device_path):
    '''
    Get a video capture device, throw if could not open.
    '''
    video_capture = cv2.VideoCapture(device_path)
    return video_capture

class HomeAlertCamera():
    '''
    A class to access a video camera using opencv
    Takes device path to video camera
    '''
    def __init__(self, device_path):
        self.video_capture = get_video_capture(device_path)
        self.video_capture.set(cv2.CAP_PROP_BUFFERSIZE, 10)
        self.frames = []
        self.frames_mutex = threading.Lock()
        self.frame_buffer_thread = threading.Thread(target=self.buffer_video_capture)
        self.frame_buffer_thread.start()


    def set_res(self, width, height):
        '''
        Set capture resolution
        '''
        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)


    def get_video_frame(self):
        '''
        Get a video frame from the buffer
        '''
        self.frames_mutex.acquire()
        if len(self.frames) == 0:
            self.frames_mutex.release()
            raise Exception('Attempted to read from empty buffer')
        img = self.frames[0]
        self.frames_mutex.release()
        return img


    def gen_video_frames(self, num_frames, fps, delay):
        '''
        Generate a number of images from the video capture given frame rate and number of frames
        delay is number of seconds (float) to sleep before getting first frame
        '''
        time.sleep(delay)
        sleep_secs = 1 / fps
        for i in range(num_frames):
            frame = self.get_video_frame()
            time.sleep(sleep_secs)
            yield frame
            

    def write_video_frames(self, dest_dir, prefix, num_frames, fps, delay, ext='.jpeg'):
        '''
        Calls gen_video_frames and writes frames to files.
        '''
        frame_num = 0
        for frame in self.gen_video_frames(num_frames, fps, delay):
            out_fname = dest_dir + '/' + prefix + '{:02d}'.format(frame_num) + ext
            cv2.imwrite(out_fname, frame)
            frame_num += 1



    def gen_video_stream(self):
        '''
        Generate a stream of frames for an html response
        '''
        while True:
            img = self.get_video_frame()
            img_str = cv2.imencode('.jpg', img)[1].tostring()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + img_str + b'\r\n\r\n')


    def buffer_video_capture(self):
        while True:
            ret, img = self.video_capture.read()
            if ret:
                self.frames_mutex.acquire()
                if len(self.frames) > 0:
                    self.frames.pop()
                self.frames.append(img)
                if len(self.frames) != 1:
                    self.frames_mutex.release()
                    raise Exception('Frame buffer must have one frame in it at all times.')
                self.frames_mutex.release()

