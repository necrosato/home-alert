import os
import subprocess
import datetime
import pytz

def photo_burst(input_device, photo_dir, fps, num_photos, width, height):
    '''
    This command shells out to ffmpeg and saves photos to a directory created in the prefix dir.
    input_device is path to video device.
    photo_dir is directory path to and save photos.
    fps is a string fraction 'frames/seconds'.
    num_photos, width, height, are all ints.
    '''
    assert (os.path.exists(input_device)),'{} does not exist.'.format(input_device)
    dims= str(width) + 'x' + str(height)
    cmd = ['ffmpeg', '-video_size', dims, '-i', input_device,
           '-vf', 'fps='+fps, '-vframes', str(num_photos), photo_dir + '/photo_%02d.jpg']
    subprocess.check_call(cmd)
