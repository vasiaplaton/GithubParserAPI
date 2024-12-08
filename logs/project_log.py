"""Module for file logging"""
import logging
from logging.handlers import TimedRotatingFileHandler

log_formatter = logging.Formatter('%(asctime)s <%(module)s> %(levelname)s '
                                  '%(funcName)s(%(lineno)d) %(message)s')
LOG_FILE = 'logs_all/service.log'

log_handler = TimedRotatingFileHandler(LOG_FILE, when="midnight", backupCount=31)

log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.INFO)
log_handler.suffix = "%Y_%m_%d"

main_logger = logging.getLogger(__name__)
main_logger.setLevel(logging.INFO)
main_logger.addHandler(log_handler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(log_formatter)
main_logger.addHandler(consoleHandler)
