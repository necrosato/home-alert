import os
import subprocess
import datetime
import pytz

def photo_burst(input_device, prefix_dir, fps, num_photos, width, height):
    '''
    This command shells out to ffmpeg and saves photos to a directory created in the prefix dir.
    input_device is path to video device.
    prefix_dir is path to create photos dir and save photos.
    fps is a string fraction 'frames/seconds'.
    num_photos, width, height, are all ints.
    '''
    time = datetime.datetime.now(pytz.timezone('America/Los_Angeles'))
    photo_dir = prefix_dir + '/' + str(time)
    os.mkdir(photo_dir)
    assert (os.path.exists(input_device)),'{} does not exist.'.format(input_device)
    dims= str(width) + 'x' + str(height)
    cmd = ['ffmpeg', '-video_size', dims, '-i', input_device,
           '-vf', 'fps='+fps, '-vframes', str(num_photos), photo_dir + '/photo_%02d.jpg']
    subprocess.check_call(cmd)
