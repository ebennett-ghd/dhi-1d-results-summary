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

import mikeio1d
from typing import List, Tuple, Union
from sys import argv
from os.path import abspath, join, split, isdir
from os import getcwd
from json import dump
import argparse
import getpass

from dpc.extraction.load_mike_file import load_file
from dpc.extraction.extract_parameters import get_data
from dpc.output.construct_spatial_file import (
    construct_csv,
    construct_formatted_csv,
    construct_geojson,
)
from dpc.utils.get_files_recursively import FileManipulation
from dpc.utils.logger import logger as log


def parse_arguments() -> Tuple[Union[None, List[str]], Union[None, str], Union[None, str], Union[None, bool]]:

    def get_file_list(path_to_file_list):
        with open(path_to_file_list, "r") as file_list_file:
            return file_list_file.read().split("\n")

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
        "-i",
        "--input-directory",
        type=str,
        help='directory of files to process',
        default=None,
        dest="input_directory",
    )

    parser.add_argument(
        "-o",
        "--output-directory",
        type=str,
        help='directory in which to save outputs',
        default=None,
        dest="output_directory",
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
        "-s",
        "--subdir",
        help='search within subdirectories for input data i.e. true',
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "-r",
        "--no-round-outputs",
        help='do not round decimal outputs to three decimal places',
        default=True,
        action="store_false",
    )

    parsed_args = parser.parse_args()

    try:
        if parsed_args.path_to_file_list is not None:
            file_paths = get_file_list(parsed_args.path_to_file_list)
        else:
            input_directory = abspath(parsed_args.input_directory)
            if isdir(input_directory):
                file_paths = get_input_paths(input_directory, parsed_args.subdir)
            else:
                log.warning(f"Input directory does not exist - using current working directory")
                file_paths = get_input_paths(getcwd(), parsed_args.recursive)

        output_directory = getcwd()
        if parsed_args.output_directory is not None:
            putative_output_directory = abspath(parsed_args.output_directory)
            if isdir(putative_output_directory):
                output_directory = putative_output_directory
            else:
                log.warning(f"Output directory does not exist - using current working directory")

        from_crs = None
        if parsed_args.from_crs is not None:
            from_crs = parsed_args.from_crs

        return file_paths, output_directory, from_crs, parsed_args.no_round_outputs
    except Exception as e:
        log.critical(f"Input arguments are not valid. Error: {e}")
        return None, None, None, None


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
        include_subdirectories=include_subdirs,
    )


def get_all_node_data(file_paths):
    """
    gets specified node data from all files
    :param file_paths: list of paths to files to include in processing - each of these files are assumed to be loadable using mikio1d
    :return:
    """
    all_node_data = []
    for file_path in file_paths:
        log.debug(f"Loading file: {file_path}")
        _, file_name = split(file_path)
        file_extension = file_name.split(".")[1].lower()
        data = load_file(file_path)

        include_nodes, include_reaches = True, False
        if file_extension == "res11":
            include_nodes, include_reaches = False, True

        all_data_from_file, projection = get_data(
            data,
            include_nodes=include_nodes,
            include_reaches=include_reaches,
        )
        for node_id, values in all_data_from_file.items():
            node_payload = {
                "file": file_name,
                "projection": projection,
                "node_id": node_id,
            }
            node_payload.update(values.items())
            all_node_data.append(node_payload)

    return all_node_data


def main(argv):

    # configuration parameters

    current_user = getpass.getuser()
    arguments = " ".join(argv)
    log.info(f"User: {current_user} calling script with inputs: {arguments}")

    file_paths, output_directory, from_crs, no_round_outputs = parse_arguments()

    if file_paths is None:
        log.critical("Check input arguments")
        return

    # get all data

    all_node_data = get_all_node_data(file_paths)

    # construct output files

    construct_csv(
        all_node_data,
        join(abspath(output_directory), "node_data"),
        round_decimals=not no_round_outputs,
    )

    construct_formatted_csv(
        all_node_data,
        join(abspath(output_directory), "formatted_node_data"),
    )

    if from_crs is not None:
        all_node_geojson = construct_geojson(
            from_crs=f"epsg:{from_crs}",
            nodes=all_node_data,
        )

        with open("inputs/test.geojson", "w") as geo_file:
            dump(all_node_geojson, geo_file)

    # construct_run_log()


if __name__ == "__main__":
    main(argv)
