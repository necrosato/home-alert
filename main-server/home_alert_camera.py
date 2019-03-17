import cv2
import time

def get_video_capture(device_path):
    '''
    Get a video capture device, throw if could not open.
    '''
    video_capture = cv2.VideoCapture(device_path)
    video_capture.read()
    return video_capture

class HomeAlertCamera():
    '''
    A class to access a video camera using opencv
    Takes device path to video camera
    '''
    def __init__(self, device_path):
        self.video_capture = get_video_capture(device_path)
        self.video_capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)


    def set_res(self, x, y):
        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, x)
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, y)


    def get_video_frame(self):
        ret, img = self.video_capture.read()
        return img


    def gen_video_frames(self, num_frames, fps):
        '''
        Generate a number of images from the video capture given frame rate and number of frames
        '''
        self.video_capture.grab()
        sleep_secs = 1 / fps
        for i in range(num_frames):
            frame = self.get_video_frame()
            time.sleep(sleep_secs)
            yield frame
            

    def write_video_frames(self, dest_dir, prefix, num_frames, fps, ext='.jpeg'):
        frame_num = 0
        for frame in self.gen_video_frames(num_frames, fps):
            out_fname = dest_dir + '/' + prefix + '{:02d}'.format(frame_num) + ext
            cv2.imwrite(out_fname, frame)
            frame_num += 1



    def gen_video_stream(self):
        '''
        Generate a stream of frames for an html response
        '''
        self.video_capture.grab()
        while True:
            img = self.get_video_frame()
            img_str = cv2.imencode('.jpg', img)[1].tostring()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + img_str + b'\r\n\r\n')
