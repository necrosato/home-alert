import ffmpeg

class HomeAlertCamera:
    '''
    A class to record hls video using ffmpeg
    Takes source path to video camera
    '''
    def __init__(self, source_path, width, height):
        self.source_path = source_path
        self.width = width
        self.height = height

    def capture(self, output_path, seconds):
        '''
        Captures for seconds, blocks calling thread until complete
        '''
        stream = ffmpeg.input(
                  self.source_path, 
                  format='v4l2',
                  input_format='mjpeg',
                  framerate=30,
                  s='{}x{}'.format(self.width, self.height),
                  t=seconds
                              )

        segment_time = 5
        list_size = seconds // segment_time
        stream = ffmpeg.output(stream,
                               output_path,
                               format='hls',
                               hls_time=segment_time,
                               hls_list_size=list_size, # keep all segments in manifest, val > 0 will cause, # keep all segments in manifest, val > 0 will cause 
                               pix_fmt='yuv420p',
                               g=30,
                               sc_threshold=0
                               )
        ffmpeg.run(stream)
