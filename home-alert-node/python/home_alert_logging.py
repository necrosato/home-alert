import logging
import sys
import time
import datetime
import os
import pathlib

COMMON_FORMAT='%(asctime)s %(levelname)s %(thread)d %(name)s %(filename)s:%(lineno)d:%(funcName)s: %(message)s'

def SetBasicLoggingConfig():
    logging.basicConfig(
            level=logging.INFO,
            format=COMMON_FORMAT,
            handlers=[
                logging.StreamHandler(sys.stdout)
                ]
            )

def GetLogger(name=__name__, level=logging.INFO, logging_dir=None, logging_format=COMMON_FORMAT):
    '''
    Create a new logging object for home alert
    Can give name for logger
    '''
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter(logging_format)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(level)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)
    if logging_dir != None:
        pathlib.Path(logging_dir).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d_%H-%M-%S')
        fname = name + '.' + timestamp + '.log'
        file_handler = logging.FileHandler(os.path.join(logging_dir, fname))
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger

def LogTimer(message='', logging_function=logging.info):
    def decorator(function):
        def wrapper(*args, **kwargs):
            start = time.time_ns()
            result = function(*args, **kwargs)
            end = time.time_ns()
            fs='{} took {} seconds : {}'
            logging_function(fs.format(function.__name__, (end-start)/1000000000, message))
            return result
        return wrapper
    return decorator
