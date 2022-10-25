import os
import subprocess

def s3_cp(src, dest):
    '''
    src should be a local dir, dest a full s3 path.
    '''
    s3_cmd = ['aws', 's3', 'cp', src, dest, '--recursive']
    subprocess.check_call(s3_cmd)

