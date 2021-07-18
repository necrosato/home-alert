import ffmpeg

class HomeAlertCamera:
    '''
    A class to record hls video using ffmpeg
    Takes source path to video camera
    '''
    def __init__(self, video_options, audio_options):
        self.video_options = video_options
        self.audio_options = audio_options 

    def capture(self, output_path, duration=None):
        '''
        Captures for seconds, blocks calling thread until complete
        '''
        if duration is None:
            duration = self.video_options['duration']
        streams = []
        streams.append(ffmpeg.input(self.video_options['source'], 
                              format='v4l2',
                              thread_queue_size=1024,
                              input_format=self.video_options['input_format'],
                              framerate=self.video_options['framerate'],
                              s='{}x{}'.format(self.video_options['width'], self.video_options['height']),
                              t=duration
                              ))
        if ('source' in self.audio_options):
            streams.append(ffmpeg.input(self.audio_options['source'], 
                                  format='alsa',
                                  channels=self.audio_options['channels'],
                                  thread_queue_size=1024,
                                  t=duration
                                  ))


        list_size = duration // self.video_options['hls_segment_time']
        stream = ffmpeg.output(*streams,
                               output_path,
                               format='hls',
                               hls_time=self.video_options['hls_segment_time'],
                               hls_list_size=list_size,
                               pix_fmt='yuv420p',
                               acodec='aac',
                               g=self.video_options['framerate'],
                               sc_threshold=0
                               )
        ffmpeg.run(stream)

