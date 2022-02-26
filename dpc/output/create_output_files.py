#!
# -*- coding: utf-8 -*-
"""
╔═╗╦ ╦╔╦╗  ╔╦╗┬┌─┐┬┌┬┐┌─┐┬
║ ╦╠═╣ ║║   ║║││ ┬│ │ ├─┤│
╚═╝╩ ╩═╩╝  ═╩╝┴└─┘┴ ┴ ┴ ┴┴─┘

Created on 2021-10-27
@author: Edmund Bennett
@email: edmund.bennett@ghd.com
"""

from typing import List, Dict, Optional
from csv import DictWriter
from pyproj import Proj

from dpc.analysis.convert_coordinate import convert_coordinate
from dpc.utils.logger import logger as log


def construct_log(
    full_file_path: str,
    description: str,
    license: str,
    user: str,
    machine_id: str,
    utc_timestamp: str,
    input_command: str,
    input_files: List[str] = None,
    critical_durations: List[str] = None,
    output_files: List[str] = None,
) -> None:
    log.debug("Calling construct_log")
    with open(full_file_path, "w") as log_file:
        log_file.write("description: " + description)
        log_file.write("\n")
        log_file.write(f"license: {license}\n")
        log_file.write(f"user: {user}\n")
        log_file.write(f"machine_id: {machine_id}\n")
        log_file.write(f"utc_timestamp: {utc_timestamp}\n")
        log_file.write(f"command: {input_command}\n")

        if input_files is not None:
            log_file.write("\n")
            log_file.write("input_files:\n")
            log_file.write("\n")
            [log_file.write(f"{input_file}\n") for input_file in input_files]

        if critical_durations is not None:
            log_file.write("\n")
            log_file.write("critical_durations:\n")
            log_file.write("\n")
            [log_file.write(f"{critical_duration}\n") for critical_duration in critical_durations]

        if output_files is not None:
            log_file.write("\n")
            log_file.write("output_files:\n")
            log_file.write("\n")
            [log_file.write(f"{output_file}\n") for output_file in output_files]


def construct_csv(
    data: List[Dict[str, any]],
    output_file_path_no_extension: str,
    ordered_data_files: List[str] = None,
    round_decimals: bool = False,
) -> None:
    log.debug("Calling construct_csv")

    preserve_order = [
        "node_id",
        "file_type",
        "projection",
        "x",
        "y",
        "invert_level",
    ]

    column_names = list(set(
        [column_name for datum in data for column_name in list(datum.keys()) if column_name not in preserve_order]
    ))
    ordered_column_names = []

    if "file" in column_names:  # ensure file is at start
        column_names.remove("file")
        preserve_order = ["file"] + preserve_order

    for data_file in ordered_data_files:
        if data_file in column_names:
            ordered_column_names.append(data_file)

    if "max_of_max_level" in column_names:  # ensure max of max is almost at the end
        column_names.remove("max_of_max_level")
        ordered_column_names.append("max_of_max_level")

    if "max_of_max_depth" in column_names:  # ensure depth is after max of max
        column_names.remove("max_of_max_depth")
        ordered_column_names.append("max_of_max_depth")

    if "critical_duration" in column_names:  # ensure critical duration is after max_of_max_depth
        column_names.remove("critical_duration")
        ordered_column_names.append("critical_duration")

    # takes data columns available for first item in list

    all_column_names = preserve_order + ordered_column_names

    if round_decimals:
        for datum in data:
            for k, v in datum.items():
                if isinstance(v, float):
                    datum[k] = round(v, 3)

    with open(output_file_path_no_extension, "w", newline="") as csv_file:
        writer = DictWriter(csv_file, fieldnames=all_column_names)
        writer.writeheader()
        writer.writerows(data)


def construct_formatted_csv(
    data: List[Dict[str, any]],
    output_file_path_no_extension: str,
    critical_durations: Dict[str, Optional[str]] = None,
    ordered_data_files: List[str] = None,
    round_decimals: bool = False,
    timings: bool = False,
) -> None:
    log.debug("Calling construct_formatted_csv")

    parameters_to_include = [
        "x",
        "y",
        "invert_level"
    ]

    def seek_data(node_id, file):
        for datum in data:
            if node_id == datum["node_id"] and file == datum["file"]:
                return datum

    # get unique list of nodes

    unique_nodes = list(set([datum["node_id"] for datum in data]))

    formatted_data = []
    for unique_node in unique_nodes:
        node_parameters_set = False
        file_maxima = []
        node_outputs = {
            "node_id": unique_node,
        }
        for i, unique_file in enumerate(ordered_data_files):
            datum = seek_data(unique_node, unique_file)
            if datum is not None and datum["max_water_level"] is not None:
                file_maxima.append(datum["max_water_level"])
            if datum is not None:
                if not node_parameters_set:
                    for param in parameters_to_include:
                        node_outputs[param] = datum[param]
                    node_parameters_set = True
                node_outputs[unique_file] = datum["max_water_level"] if not timings else datum["max_water_level_timing"]
                node_outputs["file_type"] = datum["file_type"]

        if not timings:
            node_outputs["max_of_max_level"] = None
            node_outputs["critical_duration"] = None
            if file_maxima:
                max_file_maxima = max(file_maxima)
                max_of_max_depth = max_file_maxima - node_outputs["invert_level"]
                critical_files = [s for s in node_outputs if node_outputs[s] == max_file_maxima]
                if critical_files:
                    node_outputs["critical_duration"] = critical_durations[critical_files[0]]
                node_outputs["max_of_max_level"] = max_file_maxima
                node_outputs["max_of_max_depth"] = max_of_max_depth
        formatted_data.append(
            node_outputs
        )

    construct_csv(
        formatted_data,
        output_file_path_no_extension,
        ordered_data_files=ordered_data_files,
        round_decimals=round_decimals,
    )


def construct_geojson(
    from_crs: str,
    nodes: List[Dict[str, any]],
) -> Dict[str, any]:
    log.info("Calling construct_geojson")

    geojson = {
        "type": "FeatureCollection",
        "features": []
    }

    from_crs_proj = Proj(from_crs, preserve_units=False)
    to_crs_proj = Proj("epsg:4326", preserve_units=False)

    for node in nodes:
        long, lat = convert_coordinate(
            from_crs_proj,
            to_crs_proj,
            node["x"],
            node["y"],
        )
        geojson["features"].append(
            {
                "type": "Feature",
                "properties": {
                    "file": node["file"],
                    "node_id": node["node_id"],
                    "invert_level": node["invert_level"],
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [long, lat]
                }
            }
        )

    return geojson


if __name__ == "__main__":
    pass
