"""Module for file logging"""
import logging

log_formatter = logging.Formatter('%(asctime)s <%(module)s> %(levelname)s '
                                  '%(funcName)s(%(lineno)d) %(message)s')

main_logger = logging.getLogger(__name__)
main_logger.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(log_formatter)
main_logger.addHandler(consoleHandler)
