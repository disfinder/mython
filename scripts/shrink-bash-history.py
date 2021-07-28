#!/usr/bin/env python
# -*- coding: utf-8 -*

"""
    Created by Dis Finder on 2021-07-28
    Script to remove non-uniq lines from customized bash history

    usage:
    cat ~/.bash_history | PYTHONPATH=${PYTHONPATH}:.. ./scripts/shrink-bash-history.py  -vv
"""

from lib.common import tools, prologging, config, parameters
import sys
import itertools
from collections import OrderedDict


def main():
    log = prologging.get_logger('main')
    od = OrderedDict()
    lines = sys.stdin.readlines()
    startCount = len(lines)
    lines_iter = iter(lines)
    for line1, line2 in tools.tqdmx(itertools.zip_longest(lines_iter, lines_iter), total=startCount):
        od[line2.strip('\n')] = line1.strip('\n')
    endCount = len(od.keys())*2
    log.info("Initial lines {}, result lines {}, ratio {:.2f}".format(startCount, endCount, endCount / startCount))

    for k, v in od.items():
        print(v)
        print(k)


if __name__ == '__main__':
    parser = parameters.CommonParser(descr='')
    parser.add_common()
    config.params = parser.do_parse()
    config.params.name = "SHRINK_BASH"  # name of script
    prologging.init_logging(config.params, log_params=True)
    log = prologging.get_logger('main')

    try:
        main()
        log.info('Done.')
    except KeyboardInterrupt:  # do not want to see ugly stacktrace after ctrl-c
        tools.close_tqdmx_iterators_all()
        exit(1)
