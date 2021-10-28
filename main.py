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

from typing import List, Tuple, Union
from os.path import abspath, join, split, isdir
from os import getcwd
from json import dump
import argparse

from dpc.extraction.load_mike_file import load_file
from dpc.extraction.extract_parameters import get_data
from dpc.spatial.construct_spatial_file import construct_csv, construct_geojson
from dpc.analysis.analytical_functions import extract_extrema
from dpc.utils.get_files_recursively import FileManipulation
from dpc.utils.logger import logger as log


def parse_arguments() -> Tuple[Union[None, List[str]], Union[None, str], Union[None, str]]:

    def get_file_list(path_to_file_list):
        with open(path_to_file_list, "r") as file_list_file:
            return file_list_file.read().split("\n")

    parser = argparse.ArgumentParser(description='DHI data processor')

    parser.add_argument(
        "-f",
        "--files",
        type=str,
        nargs=1,
        help='path of csv file containing list of files to process',
        default=None,
        dest="path_to_file_list",
    )

    parser.add_argument(
        "-i",
        "--input-directory",
        type=str,
        nargs=1,
        help='directory of files to process',
        default=None,
        dest="input_directory",
    )

    parser.add_argument(
        "-o",
        "--output-directory",
        type=str,
        nargs=1,
        help='directory in which to save outputs',
        default=None,
        dest="output_directory",
    )

    parser.add_argument(
        "-p",
        "--projection",
        type=str,
        nargs=1,
        help='epsg projection/coordinate reference system of input data i.e. 27200',
        default=None,
        dest="from_crs",
    )

    parsed_args = parser.parse_args()

    try:
        if parsed_args.path_to_file_list is not None:
            file_paths = get_file_list(parsed_args.path_to_file_list[0])
        else:
            input_directory = abspath(parsed_args.input_directory[0])
            if isdir(input_directory):
                file_paths = get_input_paths(input_directory)
            else:
                log.warning(f"Input directory does not exist - using current working directory")
                file_paths = get_input_paths(getcwd())

        output_directory = getcwd()
        if parsed_args.output_directory is not None:
            if isdir(parsed_args.output_directory[0]):
                output_directory = abspath(parsed_args.output_directory[0])
            else:
                log.warning(f"Output directory does not exist - using current working directory")

        return file_paths, output_directory, parsed_args.from_crs[0]
    except Exception as _:
        log.critical(f"Input arguments are not valid.")
        return None, None, None


def get_input_paths(
        input_directory: str = None,
) -> List[str]:
    """
    Gets list of input files from input directory - taking only files with appropriate file extensions
    :param input_directory: Path to a single directory
    :return: list of file paths
    """
    return FileManipulation.get_files_recursively(
        directory=input_directory,
        file_extension_allow_list=["prf"],
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
        directory_path, file_name = split(file_path)
        data, searcher = load_file(file_path)
        all_data_from_file, projection = get_data(data)
        for node_id, values in all_data_from_file.items():
            node_payload = {
                "file": file_name,
                "projection": projection,
                "node_id": node_id,
            }
            node_payload.update(values.items())
            all_node_data.append(node_payload)

    return all_node_data


def main():
    # configuration parameters

    file_paths, output_directory, from_crs = parse_arguments()

    if file_paths is None:
        return

    # get all data

    all_node_data = get_all_node_data(file_paths)

    # post-process data

    max_invert_levels = extract_extrema(
        all_node_data,
        data_parameter="invert_levels",
        aggregation_function=max,
        group_by_parameter="file",
    )

    global_max_invert_level = extract_extrema(
        all_node_data,
        data_parameter="invert_levels",
        aggregation_function=max,
    )

    # construct output files

    construct_csv(all_node_data, join(abspath(output_directory), "node_data"))
    construct_csv(max_invert_levels, join(abspath(output_directory), "max_invert_levels"))
    construct_csv(global_max_invert_level, join(abspath(output_directory), "global_max_invert_level"))

    if from_crs is not None:
        all_node_geojson = construct_geojson(
            from_crs=f"epsg:{from_crs}",
            nodes=all_node_data,
        )

        with open("test.geojson", "w") as geo_file:
            dump(all_node_geojson, geo_file)


if __name__ == "__main__":
    main()

    # path_to_geojson = "c:/Users/ebennett2/Downloads/test_fence.geojson"
    # with open(path_to_geojson, "rb") as geo_file:
    #     geo = geo_file.read()
    # shp = convert_geojson_to_shp(geo)
