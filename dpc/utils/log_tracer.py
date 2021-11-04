#!
# -*- coding: utf-8 -*-
"""
╔═╗╦ ╦╔╦╗  ╔╦╗┬┌─┐┬┌┬┐┌─┐┬
║ ╦╠═╣ ║║   ║║││ ┬│ │ ├─┤│
╚═╝╩ ╩═╩╝  ═╩╝┴└─┘┴ ┴ ┴ ┴┴─┘

Created on 2021-05-18
@author: Edmund Bennett
@email: edmund.bennett@ghd.com
"""

from os.path import isfile, split
import re
from typing import List

import dpc.utils.logger as log


class LogTracer:

    TIMESTAMP = "timestamp"
    LOG_LEVEL = "log_level"
    FILE = "file"
    LINE_NUMBER = "line_number"
    LOG_ENTRY = "log_entry"
    MISSING = "missing"

    MATCH_ORDER = [
        TIMESTAMP,
        LOG_LEVEL,
        FILE,
        LINE_NUMBER,
        LOG_ENTRY,
    ]

    MAX_LINE_WIDTH = 10

    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"

    SPLITTER = " -> "

    THIS_FILE = "log_tracer.py"

    LOG_REGEX = r"([0-9]{4}-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]:[0-5][0-9].[0-9]{3}) ([A-Z]+)\s+\[([_a-z]+\.py):([0-9]+)\] ([a-zA-Z0-9: {}\[\]',$\.(){}\-\_]+)"

    def __init__(self, path_to_log_file: str):
        log.logger.info(f"Instantiating tracer with log file: {path_to_log_file}")
        self.path_to_log_file = path_to_log_file
        self.raw_log = self._load_log()

    def _load_log(self):
        log.logger.info(f"Loading log file: {self.path_to_log_file}")
        _, file_name = split(self.path_to_log_file)
        if (
            self.path_to_log_file
            and isfile(self.path_to_log_file)
            and file_name.split(".")[-1] == "log"
        ):
            log.logger.debug(f"Log file valid")
            with open(self.path_to_log_file, "r") as log_file:
                return log_file.readlines()
        else:
            log.logger.critical(f"Log file not valid")

    def _pre_process_log_lines(
        self,
        start_timestamp: str = None,
        end_timestamp: str = None,
    ):
        processed_log = []
        for log_line in self.raw_log:

            match = re.search(
                LogTracer.LOG_REGEX,
                log_line,
            )
            if match is None:
                log.logger.warning(f"No regex match on log line: {log_line}")
                processed_log.append(
                    {
                        LogTracer.MISSING: True,
                    }
                )
            else:
                log.logger.debug(f"Match on log line: {log_line}")
                match_dict = {}
                do_append = True
                for t, m in zip(LogTracer.MATCH_ORDER, match.groups()):
                    if m is not None and m:
                        log.logger.debug(f"Match of type: {t} on element: {m}")
                        if t == LogTracer.TIMESTAMP:
                            if (
                                start_timestamp is not None and m < start_timestamp
                            ) or (end_timestamp is not None and m > end_timestamp):
                                log.logger.debug(f"Log entry not in period of interest")
                                do_append = False
                                break
                        if t == LogTracer.FILE:
                            if LogTracer.THIS_FILE == m:
                                log.logger.debug(f"Ignore calls to this file")
                                do_append = False
                                break
                        match_dict[t] = m
                    else:
                        log.logger.warning(
                            f"No match of type: {t} on element: {m} for log line: {log_line}"
                        )
                match_dict[LogTracer.MISSING] = False
                if do_append:
                    processed_log.append(match_dict)
        return processed_log

    def plot_file_trace(
        self,
        entry_point: str,
        start_timestamp: str = None,
        end_timestamp: str = None,
    ):
        """Examine the log trace"""
        log.logger.info(f"Calling get_file_trace")
        processed_log = self._pre_process_log_lines(start_timestamp, end_timestamp)
        log_entries = []
        for log_item in processed_log:
            entry = LogEntry()
            entry.parse_dict(log_item)
            log_entries.append(entry)

        features = self.get_features(
            log_levels=[
                LogTracer.DEBUG,
                LogTracer.INFO,
                LogTracer.WARNING,
                LogTracer.CRITICAL,
            ],
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            include_line_number=False,
        )

        G = nx.DiGraph()
        nodes = []
        node_sizes = []
        for location, feature in features.items():
            G.add_node(
                location,
                size=feature,
            )
            nodes.append(location)
            node_sizes.append(feature)
        cycle_start = False
        file_trace = {}
        last_file = ""
        current_depth = 0
        for log_item in processed_log:
            this_file = log_item[LogTracer.FILE]
            if last_file == this_file:
                log.logger.debug("Same file - ignore")
            else:
                if this_file != LogTracer.THIS_FILE:
                    if this_file == entry_point and not cycle_start:
                        cycle_start = True
                    if cycle_start:
                        if last_file:
                            log.logger.debug("Different file")
                            graph_path = f"{last_file}{LogTracer.SPLITTER}{this_file}"
                            current_depth += 1
                            if this_file == entry_point:
                                log.logger.debug("Entry point")
                                current_depth = 0
                            if graph_path in file_trace.keys():
                                file_trace[graph_path] += 1
                            else:
                                file_trace[graph_path] = 1
                        last_file = log_item[LogTracer.FILE]

        line_sizes = []
        for graph_path, weight in file_trace.items():
            start, end = graph_path.split(f"{LogTracer.SPLITTER}")
            G.add_edge(
                start,
                end,
                weight=weight,
            )
            line_sizes.append(min(weight, LogTracer.MAX_LINE_WIDTH))

        # log network graph

        ax = plt.gca()
        plt.title(f"Logs from: {start_timestamp} to {end_timestamp}")
        ax.set_axis_off()
        nx.draw_networkx(
            G,
            arrows=True,
            with_labels=True,
            node_size=node_sizes,
            font_size=8,
            width=line_sizes,
            alpha=0.6,
        )
        plt.draw()
        plt.show()

        # file usage bar plot

        fig, ax = plt.subplots()
        plt.title("File Usage")
        plt.xlabel("File")
        plt.ylabel("Log Count")
        plt.xticks(
            fontsize=8,
            rotation=90,
        )
        # sorted_node_sizes = sorted(node_sizes)
        # sorted_nodes = sorted(nodes, key=lambda x: index)
        # plt.bar(sorted_nodes, sorted_node_sizes)
        # plt.show()

        return file_trace

    def get_features(
        self,
        log_levels: List[str] = None,
        start_timestamp: str = None,
        end_timestamp: str = None,
        include_line_number: bool = True,
    ):
        log.logger.info(f"Calling features")
        if log_levels is None:
            log_levels = [LogTracer.WARNING, LogTracer.CRITICAL]

        processed_log = self._pre_process_log_lines(start_timestamp, end_timestamp)
        hotspots = {}
        for log_item in processed_log:
            if log_item[LogTracer.LOG_LEVEL] in log_levels:
                location = (
                    f"{log_item[LogTracer.FILE]}:{log_item[LogTracer.LINE_NUMBER]}"
                    if include_line_number
                    else log_item[LogTracer.FILE]
                )
                if location in hotspots.keys():
                    hotspots[location] += 1
                else:
                    hotspots[location] = 1

        return hotspots

    def get_counts(
        self,
        start_timestamp: str = None,
        end_timestamp: str = None,
    ):
        log.logger.info(f"Calling get_file_counts")
        processed_log = self._pre_process_log_lines(start_timestamp, end_timestamp)


if __name__ == "__main__":
    from os.path import join, expanduser

    arc_log = join(expanduser("~"), r"AppData\Local\Temp", "arc.log")
    tracer = LogTracer(path_to_log_file=arc_log)
    file_trace = tracer.plot_file_trace(
        entry_point="main.py",
        start_timestamp="2021-04-03 00:00:00.000",
        end_timestamp="2021-05-19 00:00:00.000",
    )
    print("")
