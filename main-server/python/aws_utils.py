import os
import subprocess

def s3_mv_rmdir(src, dest):
    '''
    src should be a local dir, dest a full s3 path. src will be removed.
    '''
    s3_cmd = ['aws', 's3', 'mv', src, dest, '--recursive']
    subprocess.check_call(s3_cmd)
    os.rmdir(src)

