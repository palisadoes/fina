#!/usr/bin/env python3
"""Logging module."""

import sys
import datetime
import time
import getpass
import logging


# Define global variable
LOGGER = {}


class _GetLog(object):
    """Class to manage the logging without duplicates."""

    def __init__(self, level='debug'):
        """Method initializing the class."""
        # Define key variables
        app_name = 'infoset'
        levels = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }

        # Set logging level
        log_level = levels[level]

        # create logger with app_name
        self.logger_stdout = logging.getLogger(('%s_console') % (app_name))

        # Set logging levels to  stdout
        self.logger_stdout.setLevel(log_level)

        # create console handler with a higher log level
        stdout_handler = logging.StreamHandler()
        stdout_handler.setLevel(log_level)

        # create formatter and add it to the handlers
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        stdout_handler.setFormatter(formatter)

        # add the handlers to the logger
        self.logger_stdout.addHandler(stdout_handler)

    def stdout(self):
        """Return logger for terminal IO.

        Args:
            None

        Returns:
            value: Value of logger

        """
        # Return
        value = self.logger_stdout
        return value


def log2warning(code, message):
    """Log warning message, but don't die.

    Args:
        code: Message code
        message: Message text

    Returns:
        None

    """
    # Initialize key variables
    _logit(code, message, error=False, level='warning')


def log2debug(code, message):
    """Log debug message, but don't die.

    Args:
        code: Message code
        message: Message text

    Returns:
        None

    """
    # Initialize key variables
    _logit(code, message, error=False, level='debug')


def log2info(code, message):
    """Log status message, but don't die.

    Args:
        code: Message code
        message: Message text

    Returns:
        None

    """
    # Log to screen and file
    _logit(code, message, error=False, level='info')


def log2see(code, message):
    """Log message to STDOUT, but don't die.

    Args:
        code: Message code
        message: Message text

    Returns:
        None

    """
    # Log to screen and file
    _logit(code, message, error=False)


def log2die(code, message):
    """Log to STDOUT and file, then die.

    Args:
        code: Error number
        message: Descriptive error string

    Returns:
        None
    """
    _logit(code, message, error=True)


def _logit(error_num, error_string, error=False, level='info'):
    """Log slurpy errors to file and STDOUT.

    Args:
        error_num: Error number
        error_string: Descriptive error string
        error: Is this an error or not?
        level: Logging level

    Returns:
        None

    """
    # Define key variables
    global LOGGER
    username = getpass.getuser()
    levels = ['debug', 'info', 'warning', 'error', 'critical']

    # Set logging level
    if level in levels:
        log_level = level
    else:
        log_level = 'debug'

    # Create logger if it doesn't already exist
    if bool(LOGGER) is False:
        LOGGER = _GetLog()
    logger_stdout = LOGGER.stdout()

    # Log the message
    if error:
        log_message = (
            '[%s] (%sE): %s') % (
                username, error_num, error_string)
        logger_stdout.critical('%s', log_message)

        # All done
        sys.exit(2)
    else:
        log_message = (
            '[%s] (%sS): %s') % (
                username, error_num, error_string)
        _logger_stdout(logger_stdout, log_message, log_level)


def _logger_stdout(logger_stdout, log_message, log_level):
    """Log to stdout at a particular logging level.

    Args:
        logger_stdout: stdout logger instance
        log_message: Logging message
        log_level: Logging level

    Returns:
        None

    """
    # Log accordingly
    if log_level == 'debug':
        logger_stdout.debug(log_message)
    elif log_level == 'info':
        logger_stdout.info(log_message)
    elif log_level == 'warning':
        logger_stdout.warning(log_message)
    elif log_level == 'error':
        logger_stdout.error(log_message)
    else:
        logger_stdout.critical(log_message)


def _message(code, message, error=True):
    """Create a formatted message string.

    Args:
        code: Message code
        message: Message text
        error: If True, create a different message string

    Returns:
        output: Message result

    """
    # Initialize key variables
    time_object = datetime.datetime.fromtimestamp(time.time())
    timestring = time_object.strftime('%Y-%m-%d %H:%M:%S,%f')
    username = getpass.getuser()

    # Format string for error message, print and die
    if error is True:
        prefix = 'ERROR'
    else:
        prefix = 'STATUS'
    output = ('%s - %s - %s - [%s] %s') % (
        timestring, username, prefix, code, message)

    # Return
    return output
