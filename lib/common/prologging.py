#!/usr/bin/env python
# -*- coding: utf-8 -*

"""
    Created by Dis Finder on 2018-01-10
    Simple all-in-one and easy-to-use own logging module to use standard logging and logging levels from CLI args
"""
import logging, logging.handlers
import lib.common.config
from tqdm import tqdm
import sys


class TqdmHandler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)

    def emit(self, record):
        msg = self.format(record)
        tqdm.write(msg, file=sys.stderr)


def _get_root_name(params):
    return params.name if not params.dry_run else '{}:DRY-RUN'.format(params.name)


def init_logging(params, log_params=False, add_stdout=False):
    """
    does initial logging confgigurations, as far as we need some more complicated and manageable
    :param params:
    :return:
    """

    if params.get('verbose') is None:
        # TODO: maybe just do something standard
        return
        raise Exception('verbosity not set')

    levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    params.log_level = levels[min(len(levels) - 1, params.verbose)]  # capped to number of levels
    # params.log_level_name = logging._levelNames[params.log_level]

    # doing output formatting
    sh = TqdmHandler()
    sh.setLevel(params.log_level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)8s - %(name)s - %(message)s')
    sh.setFormatter(formatter)

    root = logging.getLogger()
    root.addHandler(sh)

    if params.verbose >= 3:  # include shade debug in log. actually, not only the shade but any inherited from root
        root.setLevel(params.log_level)
    else:
        root.setLevel(logging.CRITICAL)

    # creating of our own main logging object - just to be able use debug level for our scripts and omit all the debug
    # from stadard modules like shade etc
    my_logger = logging.getLogger(_get_root_name(params))
    my_logger.addHandler(sh)
    if add_stdout:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(params.log_level)
        stdout_handler.setFormatter(formatter)
        my_logger.addHandler(stdout_handler)

    my_logger.setLevel(params.log_level)
    my_logger.propagate = False

    log = my_logger.getChild(__name__)

    if params.get('filename_log', None) is not None:  # do also log to file
        file_handler = logging.FileHandler(params.filename_log)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
        my_logger.addHandler(file_handler)

    # woho, lets use our logger
    log.debug('Logging initialization complete.')
    if log_params:  # BE CAREFUL: password can appear in logs in case it have some unobvious name!
        message = ' Parameters list:\n'
        for param in params:
            if 'password' not in param.lower():
                message += '    %30s:%40s\n' % (param, params[param])
            else:
                message += '    %30s:%40s\n' % (param, '*' * 8)
        log.debug("Parameters: %s" % message)


def get_logger(logger_name):
    """
    returns an requested logger as a child of our own root logger with same options
    for use in own classess, modules
    :param logger_name: desired name of the logger. could be simple string, or class object
    :return: logger object
    """
    root_name = _get_root_name(lib.common.config.params)
    name = logger_name
    if not isinstance(logger_name, str):
        name = "%s.%s" % (logger_name.__module__, logger_name.__class__.__name__)
    log = logging.getLogger(root_name).getChild(name)
    return log

def flush_logger(logger):
    """
    make all the handlers of logger and his parent to flush
    :param logger: logger to flush
    :return: None
    """
    for h in logger.handlers:
        h.flush()
    if logger.parent:
        for h in logger.parent.handlers:
            h.flush()
