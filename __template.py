#!/usr/bin/env python
# -*- coding: utf-8 -*

"""
    Created by Dis Finder on 2018-01-13
    Template for common operations
"""

from time import sleep
from lib.common import tools, prologging, config, parameters

def main():
    log = prologging.get_logger('main')

    for i in tools.tqdmx(range(200)):
        log.error(i)
        sleep(0.2)


if __name__ == '__main__':
    parser = parameters.CommonParser(descr='')
    parser.add_common()
    parser.add_os_basic()
    config.params = parser.do_parse()
    config.params.name = "CHANGEME"  # name of script
    prologging.init_logging(config.params, log_params=True)
    log = prologging.get_logger('module')

    try:
        main()
        log.info('Done.')
    except KeyboardInterrupt:  # do not want to see ugly stacktrace after ctrl-c
        tools.close_tqdmx_iterators_all()
        exit(1)
