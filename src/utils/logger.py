"""Bounded activity logging without student names or contact details."""
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger('sis')
    logger.setLevel(logging.INFO)
    logger.propagate = False
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
    handler = RotatingFileHandler(path, maxBytes=200000, backupCount=3, encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    logger.addHandler(handler)
    return logger
