import logging
from app.middlewares.contextmiddleware import get_request_id
import os
from app.utilities import constants


def get_logger(name,level=logging.INFO,file_name="/tmp/logs/model-inferencing-module.log"):
    """logger method to get logger from
    author: Rajesh
    Args:
        name (_type_): _description_
    Returns:
        _type_: _description_
    """
    log_format = "%(levelname)s : %(asctime)-15s %(filename)s:%(lineno)d %(funcName)-8s --> %(message)s"
    logging.basicConfig(format=log_format)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    file_handler = logging.FileHandler(file_name)
    logger.addHandler(file_handler)
    return logger


class SyneLogger(logging.LoggerAdapter):
    """Base class with logger enabled with adding a uniqueid for each request
    author: rajesh
    Args:
        logging ([type]): [description]
    """

    def process(self, msg, kwargs):
        if get_request_id() is not None:
            return '[%s] %s' % (get_request_id(), msg), kwargs
        else:
            return '%s' % (msg), kwargs
