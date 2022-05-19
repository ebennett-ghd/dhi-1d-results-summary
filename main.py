#!
# -*- coding: utf-8 -*-
"""
╔═╗╦ ╦╔╦╗  ╔╦╗┬┌─┐┬┌┬┐┌─┐┬
║ ╦╠═╣ ║║   ║║││ ┬│ │ ├─┤│
╚═╝╩ ╩═╩╝  ═╩╝┴└─┘┴ ┴ ┴ ┴┴─┘

Created on 2021-10-26
@author: Edmund Bennett
@email: edmund.bennett@ghd.com
"""

from typing import List, Tuple, Optional
from sys import argv, exit
from os.path import abspath, join, split, isdir
from os import getcwd
from json import dump
from datetime import datetime
import argparse
import getpass
import socket
import warnings

from dpc.extraction.load_mike_file import load_prf_file, load_res_file
from dpc.extraction.extract_parameters import get_data
from dpc.output.create_output_files import (
    construct_formatted_csv,
    construct_log,
    construct_geojson,
)
from dpc.utils.get_files_recursively import FileManipulation
from dpc.utils.logger import logger as log


warnings.filterwarnings("ignore")


def parse_arguments() -> Tuple[
    Optional[List[str]],
    Optional[List[Optional[str]]],
    Optional[str],
    Optional[str],
    Optional[str],
    Optional[bool],
    Optional[bool],
]:

    def get_file_list(path_to_file_list):

        with open(path_to_file_list, "r") as file_list_file:
            input_rows = [e.strip() for e in file_list_file.read().split("\n")]

            ends_of_line = []
            for input_row in input_rows:
                if input_row:
                    ends_of_line.append("")

            file_paths = [" ".join(input_row.split(" ")[:-1]) for input_row in input_rows if input_row]

            critical_durations = []
            for i, (start_of_line, file) in enumerate(zip(file_paths, input_rows)):
                if start_of_line:
                    critical_durations.append(file.replace(start_of_line, "").strip())
                else:
                    file_paths[i] = file
                    critical_durations.append(None)

            return file_paths, critical_durations

    parser = argparse.ArgumentParser(description='DHI data processor')

    parser.add_argument(
        "-f",
        "--files",
        type=str,
        help='path of csv file containing list of files to process',
        default=None,
        dest="path_to_file_list",
    )

    parser.add_argument(
        "-o",
        "--output-name",
        type=str,
        help='filename for outputs (do not include file extension) and optional directory in which to save outputs in format directory/filename',
        default=None,
        dest="output_directory_and_name",
    )

    parser.add_argument(
        "-p",
        "--projection",
        type=str,
        help='epsg projection/coordinate reference system of input data i.e. 27200',
        default=None,
        dest="from_crs",
    )

    parser.add_argument(
        "-i",
        "--input-directory",
        type=str,
        help='directory of files from which to generate file list',
        default=None,
        dest="input_directory",
    )

    parser.add_argument(
        "-s",
        "--subdir",
        help='search within subdirectories for input data i.e. true - used with --input-directory to generate list of files to process',
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "-l",
        "--create-file-list",
        help='create a list of files to be processed',
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "-r",
        "--no-round-outputs",
        help='do not round decimal outputs to three decimal places',
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "-t",
        "--include-timings",
        help='include separate timing output file indicating timestep of maximum water levels',
        default=False,
        action="store_true",
    )

    parsed_args = parser.parse_args()
    critical_durations = None

    try:
        if parsed_args.path_to_file_list is not None:
            file_paths, critical_durations = get_file_list(parsed_args.path_to_file_list)
        else:
            input_directory = abspath(parsed_args.input_directory)
            if isdir(input_directory):
                file_paths = get_input_paths(input_directory, parsed_args.subdir)
            else:
                log.warning(f"Input directory does not exist - using current working directory")
                file_paths = get_input_paths(getcwd(), parsed_args.recursive)

        output_directory = getcwd()
        if any(e in parsed_args.output_directory_and_name for e in ["\\", "/"]):  # then directory present
            putative_output_directory, output_filename = split(parsed_args.output_directory_and_name)
            if isdir(putative_output_directory):
                output_directory = putative_output_directory
        else:
            output_filename = parsed_args.output_directory_and_name

        if output_directory == getcwd():
            log.warning(f"Output directory does not exist - using current working directory")
            output_filename = "input_files"

        from_crs = None
        if parsed_args.from_crs is not None:
            from_crs = parsed_args.from_crs

        if parsed_args.path_to_file_list is None and parsed_args.create_file_list:
            with open(join(output_directory, f"{output_filename}.txt"), "w") as inputs_file:
                for i, file_path in enumerate(file_paths):
                    payload = file_path + "\n" if i < len(file_paths) - 1 else file_path
                    inputs_file.writelines(payload)
                exit()

        return (
            file_paths,
            critical_durations,
            output_directory,
            output_filename,
            from_crs,
            parsed_args.no_round_outputs,
            parsed_args.include_timings,
        )

    except Exception as e:
        log.critical(f"Input arguments are not valid. Error: {e}")
        return None, None, None, None, None, None, None


def get_input_paths(
    input_directory: str = None,
    include_subdirs: bool = False,
) -> List[str]:
    """
    Gets list of input files from input directory - taking only files with appropriate file extensions
    :param input_directory: Path to a single directory
    :return: list of file paths
    """
    return FileManipulation.get_files_recursively(
        directory=input_directory,
        file_extension_allow_list=["prf", "res11"],
        exclude_filename_text="HDADD",
        include_subdirectories=include_subdirs,
    )


def get_all_node_data(
    file_paths: List[str],
):
    """
    gets specified node data from all files
    :param file_paths: list of paths to files to include in processing - each of these files are assumed to be loadable using mikio1d
    :param critical_durations: list of critical durations to include in processing - ordered list expected in the same order as files
    :return: node data
    """
    all_node_data = []
    for file_path in file_paths:
        include_nodes, include_reaches = True, True
        if file_path:
            log.debug(f"Loading file: {file_path}")
            _, file_name = split(file_path)
            split_row = file_name.split(".")
            file_extension = split_row[1].lower()

            data, df = None, None
            if file_extension == "res11":
                data, df = load_res_file(file_path)
                include_nodes = False
            elif file_extension == "prf":
                data, df = load_prf_file(file_path)
                include_reaches = False

            if data is not None:
                all_data_from_file, projection = get_data(
                    data,
                    df=df,
                    include_nodes=include_nodes,
                    include_reaches=include_reaches,
                )

                for node_id, values in all_data_from_file.items():
                    node_payload = {
                        "file": file_name,
                        "file_type": file_extension,
                        "projection": projection,
                        "node_id": node_id,
                    }
                    node_payload.update(values.items())
                    all_node_data.append(node_payload)

    return all_node_data


def main(argv):

    # configuration parameters

    description = """DHI 1D points - extraction tool - log file.
    
This log file is generated by the DHI 1D points extraction tool version 1.0.0 which was last updated on 2022-05-18.
The tool was developed as open source code by GHD. This log file captures tool input parameters and outputs generated.

If the CSV output file is converted to spatial format (eg: SHP, GEOJSON) then this log file should be copied into the spatial metadata.
If the CSV output file is converted to spreadsheet format then this log file should be copied into a separate 'readme' tab.
"""

    current_user = getpass.getuser()
    arguments = " ".join(argv)
    log.info(f"User: {current_user} calling script with inputs: {arguments}")

    (
        file_paths,
        critical_durations,
        output_directory,
        output_filename,
        from_crs,
        no_round_outputs,
        include_timings,
     ) = parse_arguments()

    if output_filename is None:
        output_filename = "formatted_node_data"

    log_payload = {
        "description": description,
        "license": "TBC",
        "user": current_user,
        "machine_id": socket.gethostname(),
        "utc_timestamp": str(datetime.utcnow()),
        "command": arguments,
        "input_files": file_paths,
        "critical_durations": critical_durations,
    }

    with open(join(output_directory, f"{output_filename}.log"), "w") as log_file:
        dump(log_payload, log_file, indent=4)

    if file_paths is None:
        log.critical("Check input arguments")
        return

    if critical_durations is None:
        critical_durations = [None for _ in range(len(file_paths))]

    critical_duration_dict = {}
    for file, duration in zip(file_paths, critical_durations):
        file_path, file_name = split(file)
        critical_duration_dict[file_name] = duration

    # get all data

    all_node_data = get_all_node_data(file_paths)

    # construct output files

    # construct_csv(  # uncomment this to produce an un-formatted output
    #     data=all_node_data,
    #     output_file_path_no_extension=join(abspath(output_directory), "node_data"),
    #     round_decimals=not no_round_outputs,
    # )

    construct_formatted_csv(
        data=all_node_data,
        output_file_path_no_extension=join(abspath(output_directory), f"{output_filename}.csv"),
        critical_durations=critical_duration_dict,
        ordered_data_files=[split(e)[-1] for e in file_paths],
        round_decimals=not no_round_outputs,
        timings=False,
    )

    output_files = [
        abspath(join(output_directory, f"{output_filename}.csv")),
        abspath(f"{output_filename}.log"),
    ]
    if include_timings:
        construct_formatted_csv(
            data=all_node_data,
            output_file_path_no_extension=join(abspath(output_directory), f"{output_filename}_timing.csv"),
            critical_durations=critical_duration_dict,
            ordered_data_files=[split(e)[-1] for e in file_paths],
            round_decimals=not no_round_outputs,
            timings=True,
        )

        output_files = [
            abspath(join(output_directory, f"{output_filename}.csv")),
            abspath(join(output_directory, f"{output_filename}_timing.csv")),
            abspath(join(output_directory, f"{output_filename}.log")),
        ]

    if from_crs is not None:
        all_node_geojson = construct_geojson(
            from_crs=f"epsg:{from_crs}",
            nodes=all_node_data,
        )

        with open(join(output_directory, f"{output_filename}.geojson"), "w") as geo_file:
            dump(all_node_geojson, geo_file)
        output_files.append(join(output_directory, abspath(f"{output_filename}.geojson")))

    log_payload["output_files"] = output_files

    with open(join(output_directory, f"{output_filename}.log"), "w") as log_file:
        dump(log_payload, log_file, indent=4)

    construct_log(
        full_file_path=join(output_directory, f"{output_filename}.log"),
        description=log_payload["description"],
        license=log_payload["license"],
        user=log_payload["user"],
        machine_id=log_payload["machine_id"],
        utc_timestamp=log_payload["utc_timestamp"],
        input_command=log_payload["command"],
        input_files=log_payload["input_files"],
        critical_durations=log_payload["critical_durations"],
        output_files=log_payload["output_files"],
    )


if __name__ == "__main__":
    main(argv)
