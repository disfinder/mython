#!/usr/bin/env python
# -*- coding: utf-8 -*

"""
    Created by Dis Finder on 2018-01-10
    All the parameters options and related data (formats and parsing classes)
"""
import argparse
from enum import Enum
from munch import Munch
import lib.common.config as config
import getpass

from datetime import datetime, timedelta
from pytimeparse import parse as timeparse


def _round_time(dt=None, round_to=60):
    if dt == None:
        dt = datetime.now()
    seconds = (dt - dt.min).seconds
    rounding = (seconds + round_to / 2) // round_to * round_to
    return dt + timedelta(0, rounding - seconds, -dt.microsecond)


class OutputFormat(Enum):
    """
    class represents possible output formats.
    """
    tabulated = 'tabulated'
    csv = 'csv'
    plain = 'plain'
    json = 'json'
    prehtml = 'prehtml'
    # names with t_ = implemented with tabulate format
    t_fancy = 't_fancy'
    t_jira = 't_jira'
    t_html = 't_html'
    t_html_no_wrap = 't_html_no_wrap'


    def __str__(self):
        return self.name


def QouteTrimmer(st):
    """ strip quotes from parameters values in case they are present"""
    return str(st).strip('\'').strip('\"')


class PasswordPromptAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values is None:
            password = getpass.getpass()
        else:
            password = values
        setattr(namespace, self.dest, password)


class CommonParser:
    """main class for parsing.
    usage example:
        parser = parameters.CommonParser(descr='Blah-blah. Blah.')
        parser.add_basic()
        parser.add_input()
        cfg.params = parser.do_parse()
    """

    def __init__(self, descr='Common parser', show_defaults=True):
        self.parser = argparse.ArgumentParser(description=descr,
                                              formatter_class=argparse.ArgumentDefaultsHelpFormatter if show_defaults else argparse.HelpFormatter)
        self.name = config.name

    def do_parse(self):
        """
        do actual parsing
        :return:
        munch of parsed arguments, because munch in more usable than standard namespace in argparse
        """
        result = Munch({})
        result.update(config.params)
        parser = self.parser
        result.update(vars(parser.parse_args()))
        result['name'] = self.name

        if result.get('output_format') is not None:
            if result.output_format == OutputFormat.csv.value and result.output_filename is None:
                parser.error('In case output format = csv, then \'-o filename\' is required')

        if result.get('tag_name'):
            try:
                result.metadata = {item.split('=')[0]: item.split('=')[1] for item in result.tag_name}
            except Exception as e:
                raise Exception("Error parsing metadata, should pass it in 'key=value' format. Error: %s" % e.message)

        # lets parce hosts:port in case they are present
        # change from list of string to list of tuples (host,port)
        if result.get('host'):
            hosts_list = []
            hosts = result['host']
            if isinstance(hosts, list):
                for host in hosts:
                    parced_string = host.split(':')
                    hostname = parced_string[0]
                    port = 80 if len(parced_string) == 1 else parced_string[1]
                    hosts_list.append((hostname, port))
                result['hosts'] = hosts_list
            else:
                result['hosts'] = [(result.host, result.port)]

        if result.get('moment_stop'):  # we have timing group, lets deal with it
            seconds = result.interval.total_seconds()
            if result.make_moments_aligned:
                result.moment_stop = _round_time(result.moment_stop, seconds)
            if result.moment_start is None:  # in case start not defined, do math
                result.moment_start = result.moment_stop - result.interval
            else:
                if result.make_moments_aligned:
                    result.moment_start = _round_time(result.moment_start, seconds)

            # also lets set JSON-formatted moments
            result.json_moment_start = result.moment_start.isoformat() + 'Z'
            result.json_moment_stop = result.moment_stop.isoformat() + 'Z'

        return result

    def add_credentials(self):
        parser = self.parser.add_argument_group('Credentials')
        parser.add_argument('-u', '--username', required=True, action='store',
                            help='User name to use when connecting to host.')
        parser.add_argument('-p', '--password', required=True, action=PasswordPromptAction, nargs='?',
                            help='Password to use when connecting to host.')

    def add_host_port(self, default_host=None, default_port=443):
        parser = self.parser.add_argument_group('Endpoint connection')
        parser.add_argument('-s', '--host', required=(default_host is None), action='store',
                            help='Remote host to connect to', default=default_host)
        parser.add_argument('-o', '--port', type=int, default=default_port, action='store',
                            help='Port to connect on')

    def add_hosts(self):
        parser = self.parser.add_argument_group('Endpoint connection list')
        parser.add_argument('-s', '--host', required=True, action='append',
                            help='Remote host to connect to, can be repeated.')

    def add_basic(self):  # TODO: looks like this basic name is not good for non-P9 scripts, so....
        """
        DEPRECATED
        adds basic parameters to parser, like cloud name, region, verbosity or so
        :return:
        """
        self.add_common()
        self.add_os_basic()

    def add_os_basic(self):
        parser = self.parser
        parser.add_argument('-c', '--cloud-name', dest='cloud_names', action='append', default=None, required=False,
                            help='Cloud names from clouds.yaml or environment variables. Can be repeated.')
        parser.add_argument('-f', '--filename-clouds', dest='filename_clouds', action='append',
                            help='Filename for clouds.yaml', default=None, required=False)
        parser.add_argument('-r', '--region', dest='region_names', required=False, action='append',
                            help='Specify regions to work with, or \'all\'. Can be repeated.')

    def add_common(self):
        group_common = self.parser.add_argument_group('Verbosity maniplutation')

        group_common.add_argument('-v', '--verbose', action='count', default=0, help='verbosity level, up to -vvv')
        group_common.add_argument('--no-progress', action='store_true', dest='progressbar_disabled',
                                  help='Progressbar disabled.')
        group_common.add_argument('-fl', '--filename-log', dest='filename_log', metavar='stderr.log',
                                  default=None, help='File with additional logging.')

    def add_input(self):
        """
        adds input parameters to parser, because several scripts will require same files.
        TODO: rename to add_costs_input()
        :return:
        """
        parser = self.parser
        group_input = parser.add_argument_group('Input files', 'Input files with reference information')
        group_input.add_argument('-fc', '--filename-costs', dest='filename_costs', metavar='costs.yaml',
                                 default='refs/costs.yaml', help='File with costs data.')
        group_input.add_argument('-ft', '--filename-tags', dest='filename_tags', metavar='tags.yaml',
                                 default='refs/tags.yaml', help='File with tags data')
        group_input.add_argument('-fm', '--filename-metadata,', dest='filename_metadata', metavar='metadata.yaml',
                                 default='refs/metadataDefinition.yaml', help='File with application metadata scheme.')

    def add_output_format(self):

        output = self.parser.add_argument_group('Output', 'List of options to specify output process')
        output.add_argument('-of', '--output-format', dest='output_format', default=OutputFormat.tabulated,
                            choices=list(OutputFormat), type=OutputFormat,
                            help='Output file format: comma-separated values, JSON, plain text or pretty table.')

    def add_output(self):
        """
        adds output parameters to parser, because MAYBE several scripts will require same files. need to think
        TODO: rename to add_costs_output()
        :return:
        """
        parser = self.parser
        output = parser.add_argument_group('Output', 'List of options to specify output process')
        output.add_argument('-of', '--output-format', dest='output_format', default=OutputFormat.tabulated,
                            choices=list(OutputFormat), type=OutputFormat,
                            help='Output file format: comma-separated values, JSON, plain text or pretty table.')

        output.add_argument('-om', '--output-main', dest='output_filename',
                            help='Where to write output of main report', default='-')

        output.add_argument('-ou', '--output-untagged', dest='output_filename_untagged',
                            help='Where to write output of untagged data report', default='-')

        output.add_argument('-or', '--output-raw', dest='output_filename_raw',
                            help='Where to write output of raw data report', default='/dev/null')

    def add_grep(self):
        parser = self.parser
        grep = parser.add_argument_group('Grep', 'Grep (filtering) options')
        grep.add_argument('-gr', '--filter', dest='grep_regexp', required=False, default='.*', type=QouteTrimmer,
                          help='regexp for filter')
        grep.add_argument('-gc', '--column', dest='grep_column', required=False, default='name', type=QouteTrimmer,
                          help='column name for filter')

    def add_dryrun(self):
        # add_argument_group()
        self.parser.add_argument('-n', '--dry-run', dest='dry_run', required=False, action='store_true',
                                 help='not make actual changes, just dry-run')

    def add_logs_also_to_stdout(self):
        # add_argument_group()
        self.parser.add_argument('--add-log-to-stdout', dest='add_log_to_stdout', required=False, action='store_true',
                                 help='Make logging both to stderr and to stdout')

    def add_tags(self):
        self.parser.add_argument('-t', '--tag', dest='tag_name', required=True, action='append', metavar='name=value',
                                 help='Tag name and value, repeat for multiply tags.', type=QouteTrimmer)

    def add_mock(self):
        self.parser.add_argument('--use-tricky-mock', help=argparse.SUPPRESS, action='store_true')

    def add_timing(self, format=config.MOMENT_FORMAT):
        timing_group = self.parser.add_argument_group('Timing')
        timing_group.add_argument("--moment-start", type=lambda x: datetime.strptime(x, format),
                                  help="Start moment", required=False, default=None)
        timing_group.add_argument("--moment-stop", type=lambda x: datetime.strptime(x, format),
                                  help="Stop moment", required=False, default=datetime.now())
        timing_group.add_argument("--interval", type=lambda x: timedelta(seconds=timeparse(x)),
                                  help="Interval, will be deducted from stop to find start. If start passed explicitly, then ignored.",
                                  required=False, default=timedelta(days=1))
        timing_group.add_argument("--make-moments-aligned", action='store_true',
                                  help="Make or not alignment of the moments to the beginning and end of the interval")


    def add_z_hostname(self):
        zabbix_group = self.parser.add_argument_group('Zabbix')
        zabbix_group.add_argument('-zh', '--zabbix-host', dest='zabbix_host', required=True, type=QouteTrimmer,
                                  help='Zabbix host regexp to deal with')

    def add_z_groupname(self):
        zabbix_group = self.parser.add_argument_group('Zabbix')
        zabbix_group.add_argument('-zg', '--zabbix-group', dest='zabbix_group', required=True, type=QouteTrimmer,
                                  help='Zabbix group regexp to deal with')

    def add_data_list(self):
        parser = self.parser.add_argument_group('Data list to work with')
        parser.add_argument('-l', '--list', dest='data_list', required=True, action='append',
                            help='Data for processing, can be repeated.', type=QouteTrimmer)

    def add_named_data_list(self, short_key, long_key, dest):
        # parser = self.parser.add_argument_group('Data list to work with')
        self.parser.add_argument(short_key, long_key, dest=dest, required=True, action='append',
                            help='Data for processing, can be repeated.', type=QouteTrimmer)
