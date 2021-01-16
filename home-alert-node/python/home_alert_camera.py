import ffmpeg

class HomeAlertCamera:
    '''
    A class to record hls video using ffmpeg
    Takes source path to video camera
    '''
    def __init__(self, options):
        self.options = options

    def capture(self, output_path, duration=None):
        '''
        Captures for seconds, blocks calling thread until complete
        '''
        if duration is None:
            duration = self.options['duration']
        stream = ffmpeg.input(self.options['source'], 
                              format='v4l2',
                              input_format=self.options['input_format'],
                              framerate=self.options['framerate'],
                              s='{}x{}'.format(self.options['width'], self.options['height']),
                              t=duration
                              )

        list_size = duration // self.options['hls_segment_time']
        stream = ffmpeg.output(stream,
                               output_path,
                               format='hls',
                               hls_time=self.options['hls_segment_time'],
                               hls_list_size=list_size,
                               pix_fmt='yuv420p',
                               g=self.options['framerate'],
                               sc_threshold=0
                               )
        ffmpeg.run(stream)
