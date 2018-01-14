#!/usr/bin/env python
# -*- coding: utf-8 -*

"""
    Created by Dis Finder on 2018-01-14
    Template for common operations: all in one version
"""

from time import sleep
import logging as log
import argparse
from tqdm import tqdm
import sys

iterators_for_closing = []


def parse_args():
    parser = argparse.ArgumentParser(description='', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    group_common = parser.add_argument_group('Verbosity maniplutation')

    group_common.add_argument('-v', '--verbose', action='count', default=0, help='verbosity level, up to -vvv')
    group_common.add_argument('--show-progress', action='store_true', dest='show_progressbar',
                              help='Show tqdm progressbar.')

    group_common.add_argument('-fl', '--filename-log', dest='filename_log', metavar='stderr.log',
                              default=None, help='File with additional logging.')
    args = parser.parse_args()

    levels = [log.WARNING, log.INFO, log.DEBUG]
    args.log_level = levels[min(len(levels) - 1, args.verbose)]  # capped to number of levels

    return args


class TqdmHandler(log.StreamHandler):
    def __init__(self):
        log.StreamHandler.__init__(self)

    def emit(self, record):
        msg = self.format(record)
        tqdm.write(msg, file=sys.stderr)


def tqdmx(iterable, desc=None, **kwargs):
    if hasattr(iterable, '__len__'):
        if len(iterable) <= 1:
            return iterable
    iterator = tqdm(iterable=iterable, desc=desc, disable=args.show_progressbar, leave=False,
                    **kwargs)
    iterators_for_closing.append(iterator)
    return iterator


def close_tqdmx_iterators_all():
    for iterator in iterators_for_closing:
        iterator.close()


def main(args):
    for i in tqdmx(range(200)):
        log.error(i)
        sleep(0.2)
    return args


if __name__ == '__main__':
    args = parse_args()
    log.basicConfig(level=args.log_level)
    sh = TqdmHandler()
    sh.setLevel(args.log_level)
    formatter = log.Formatter('%(asctime)s - %(levelname)8s - %(name)s - %(message)s')
    sh.setFormatter(formatter)

    root = log.getLogger()
    root.addHandler(sh)

    if args.verbose >= 3:  # include shade debug in log. actually, not only the shade but any inherited from root
        root.setLevel(args.log_level)
    else:
        root.setLevel(log.CRITICAL)
    my_logger = log.getLogger('NAME')
    my_logger.addHandler(sh)

    my_logger.setLevel(args.log_level)
    my_logger.propagate = False

    log = my_logger.getChild(__name__)

    try:
        result = main(args)
        log.info('Done.')
    except KeyboardInterrupt:  # do not want to see ugly stacktrace after ctrl-c
        close_tqdmx_iterators_all()
        exit(1)
