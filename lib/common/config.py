#!/usr/bin/env python
# -*- coding: utf-8 -*

"""
    Created by Dis Finder on 2018-01-10
    constants, configuration, all the immutable and mutable data, shared between modules.
"""
from munch import Munch

WRONG_PROJECT_PATTERN = '\w{32}-\w{8}-\w{4}-\w{4}-\w{4}-\w{7}'  # projects in OpenStack we want to skip

name = 'main'  # used for logging
params = Munch({'dry_run':False})  # will be filled with argparse, could contain any defaults

# KBFACTOR = long(1 << 10)
# MBFACTOR = long(1 << 20)
# GBFACTOR = long(1 << 30)
#
MOMENT_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
DATE_FORMAT = '%Y-%m-%d'

iterators_for_closing = []
