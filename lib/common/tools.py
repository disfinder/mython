#!/usr/bin/env python
# -*- coding: utf-8 -*

"""
    Created by Dis Finder on 2018-01-10
    TODO: fill modude doc
"""
import munch
import yaml
import sys
import contextlib
from tabulate import tabulate
from collections import OrderedDict
from tqdm import tqdm
from lib.common.config import params
from lib.common.parameters import OutputFormat
import lib.common.config


def pprint_dict(dictionary, need_sort=True, indent_size=0):
    """
    pretty printing for dictionary with keys
    :param indent_size: space indentation in the begining
    :param need_sort: to sort or not keys
    :param dictionary:
    :return:
    """
    indent = " " * indent_size
    longest_key = max(len(k) for k in dictionary)
    if need_sort:
        keys = sorted(dictionary.keys())
    else:
        keys = dictionary.keys()
    for k in keys:
        # print wrapper.fill("{indent}{key:{width}} :{value}".format(indent=indent, key=k, value=dictionary[k],
        #                                                            width=longest_key))
        print (u"{indent}{key:{width}} :{value}".format(indent=indent, key=k, value=dictionary[k],
                                                       width=longest_key))


def get_data_from_yaml(filename):
    # we will not check for file existance, in case file is absent - exception is the best choice
    f = file(filename)
    y = yaml.load(f)
    if not isinstance(y, dict):  # we expecting ONLY dict here
        raise Exception('Yaml content must be a dictionary.')
    return munch.Munch(y)


def get_dict_from_list(initial_list, keyname='id'):
    """
    transforms list of dicts into dict of dicts with  keyname as key
    :param initial_list:
    :param keyname:
    :return:
    """
    return {value[keyname]: value for value in initial_list}


@contextlib.contextmanager
def smart_open(filename=None):
    if filename and filename != '-':
        fh = open(filename, 'w')
    else:
        fh = sys.stdout

    try:
        yield fh
    finally:
        if fh is not sys.stdout:
            fh.close()


def tabulate_data(data, columns_dict, tablefmt=None):
    """
    :param data: list of dicts
    :param columns_dict: map, containing correspondence between dict key and table header
    :return: tabulated data, ready for output with requested parameters
    """
    cropped = []
    for item in data:
        sub_dict = OrderedDict()
        for key in columns_dict.keys():
            value = item.get(key)
            sub_dict[key] = value
        cropped.append(sub_dict)
    return tabulate(cropped, headers=columns_dict, tablefmt=tablefmt)


def get_number_of_lines_in_file(file_path):
    count = 0
    with open(file_path, 'r') as f:
        for line in f:
            count += 1
    return count


def tqdmx(iterable, desc=None, **kwargs):
    if hasattr(iterable, '__len__'):
        if len(iterable) <= 1:
            return iterable
    iterator = tqdm(iterable=iterable, desc=desc, disable=lib.common.config.params.progressbar_disabled, leave=False,
                    **kwargs)
    lib.common.config.iterators_for_closing.append(iterator)
    return iterator


def close_tqdmx_iterators(iterators_list):
    for i, iterator in enumerate(iterators_list):
        iterator.close()


def close_tqdmx_iterators_all():
    for iterator in lib.common.config.iterators_for_closing:
        iterator.close()


def is_true_false_or_none(param):
    """
    tests if the passed param is true, false or none. only mentioned values can be true, only mentioned can
    be false and all other are none
    :param param:
    :return:
    """
    true_list = ['true', 'yes', '1', True, 1]
    false_list = ['false', 'no', '0', False, 0]
    test_value = param

    if isinstance(param, str):
        test_value = param.lower()

    if test_value in true_list:
        return True
    elif test_value in false_list:
        return False
    else:
        return None


def format_output(data, headers, format_as):
    """
    :param data: list of dictionaries
    :param headers: dict where key==key in list, value - header
    :param format_as: how to format data
    :return: formatted data
    """
    if format_as == OutputFormat.tabulated:
        return tabulate_data(data, headers)
    if format_as == OutputFormat.t_fancy:
        return tabulate_data(data, headers, tablefmt='fancy_grid')
    if format_as == OutputFormat.t_jira:
        return tabulate_data(data, headers, tablefmt='jira')
    if format_as == OutputFormat.t_html:
        return tabulate_data(data, headers, tablefmt='html')
    if format_as == OutputFormat.t_html_no_wrap:
        return tabulate_data(data, headers, tablefmt='html').replace('<tr>', '<tr style="white-space: nowrap;">')

    # TODO: need to sanitize or escape data for CSV format or use library.
    # TODO: At this moment, libraryies require file for write to
    if format_as == OutputFormat.csv:
        result = ",".join(headers.values())
        for item in data:
            result += '\n'
            result += ",".join(['"{}"'.format(item[k]) for k in headers.keys()])
        return result

    if format_as == OutputFormat.plain:
        result = ''
        for item in data:
            result += " ".join(['"{}"'.format(item[k]) for k in headers.keys()])
            result += '\n'
        return result

    raise Exception('Output format \'{}\' not implemented'.format(format_as))


def format_output_list(list_data_headers, format_as):
    """
    :param list_data_headers: list of tuples of (data, headers, name)
    :param format_as:
    :return: formatted data
    """


    prefix = ''  # custom beginning for each output format
    name_format = ''
    section_delimiter = ''

    if format_as == OutputFormat.tabulated:
        name_format = '{} ' + '*' * 40
        section_delimiter = '\n'
    if format_as == OutputFormat.t_fancy:
        name_format = '{} ' + '*' * 40 + '\n'
        section_delimiter = '\n'
    if format_as == OutputFormat.t_jira:
        name_format = '\n'
    if format_as == OutputFormat.t_html:
        prefix = '<ac:structured-macro ac:name="toc"/>'
        name_format = '<h1>{}</h1>'
    if format_as == OutputFormat.t_html_no_wrap:
        prefix = '<ac:structured-macro ac:name="toc"/>'
        name_format = '<h1>{}</h1>'
    if format_as == OutputFormat.csv:
        name_format = ''
        section_delimiter = '\n'

    formatted_sections = []
    for data, headers, name in list_data_headers:
        name = name_format.format(name)
        section = format_output(data, headers, format_as)
        formatted_sections.append(u"{}{}".format(name, section))

    result = u"{}{}".format(prefix, section_delimiter.join(formatted_sections))
    return result


def safe_div(nom, denom, result=-1):
    return nom / denom if denom != 0 else result


def safe_round(nom, denom, result=-1, digits=1):
    return round(safe_div(nom, float(denom), result), digits)


def multikeysort(items, columns):
    from operator import itemgetter
    comparers = [((itemgetter(col[1:].strip()), -1) if col.startswith('-') else
                  (itemgetter(col.strip()), 1)) for col in columns]

    def comparer(left, right):
        for fn, mult in comparers:
            result = cmp(fn(left), fn(right))
            if result:
                return mult * result
        else:
            return 0

    return sorted(items, cmp=comparer)
