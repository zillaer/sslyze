# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import sys
from io import open
from typing import Type, Any, Set, List

from sslyze.cli import FailedServerScan, CompletedServerScan
from sslyze.cli.console_output import ConsoleOutputGenerator
from sslyze.cli.json_output import JsonOutputGenerator
from sslyze.cli.output_generator import OutputGenerator
from sslyze.cli.xml_output import XmlOutputGenerator
from sslyze.plugins.plugin_base import Plugin
from sslyze.server_connectivity import ServerConnectivityInfo


class OutputHub(object):
    """Configure the SSLyze CLI's output and forward notification of events to all enabled output generators.
    """
    def __init__(self):
        # type: () -> None
        self._output_generator_list = []  # type: List[OutputGenerator]

    def command_line_parsed(self, available_plugins, args_command_list):
        # type: (Set[Type[Plugin]], Any) -> None
        # Configure the console output
        should_print_text_results = not args_command_list.quiet and args_command_list.xml_file != '-' \
                                    and args_command_list.json_file != '-'
        if should_print_text_results:
            self._output_generator_list.append(ConsoleOutputGenerator(sys.stdout))

        # Configure the JSON output
        if args_command_list.json_file:
            json_file_to = sys.stdout if args_command_list.json_file == '-' else open(args_command_list.json_file, 'wt')
            self._output_generator_list.append(JsonOutputGenerator(json_file_to))  # type: ignore

        # Configure the XML output
        if args_command_list.xml_file:
            xml_file_to = sys.stdout if args_command_list.xml_file == '-' else open(args_command_list.xml_file, 'wt')
            self._output_generator_list.append(XmlOutputGenerator(xml_file_to))  # type: ignore

        # Forward the notification
        for out_generator in self._output_generator_list:
            out_generator.command_line_parsed(available_plugins, args_command_list)

    def server_connectivity_test_failed(self, failed_scan):
        # type: (FailedServerScan) -> None
        for out_generator in self._output_generator_list:
            out_generator.server_connectivity_test_failed(failed_scan)

    def server_connectivity_test_succeeded(self, server_connectivity_info):
        # type: (ServerConnectivityInfo) -> None
        for out_generator in self._output_generator_list:
            out_generator.server_connectivity_test_succeeded(server_connectivity_info)

    def scans_started(self):
        # type: () -> None
        for out_generator in self._output_generator_list:
            out_generator.scans_started()

    def server_scan_completed(self, server_scan_result):
        # type: (CompletedServerScan) -> None
        for out_generator in self._output_generator_list:
            out_generator.server_scan_completed(server_scan_result)

    def scans_completed(self, total_scan_time):
        # type: (float) -> None
        # Forward the notification and close all the file descriptors
        for out_generator in self._output_generator_list:
            out_generator.scans_completed(total_scan_time)
            out_generator.close()

