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

from typing import List, Dict
from csv import DictWriter
from pyproj import Proj, transform

from dpc.utils.logger import logger as log


def construct_csv(
    data: List[Dict[str, any]],
    output_file_path_no_extension: str,
    round_decimals: bool = False,
):
    log.info("Calling construct_csv")

    preserve_order = [
        "node_id",
        "projection",
        "x",
        "y",
        "invert_level",
    ]

    column_names = list(set([column_name for datum in data for column_name in list(datum.keys()) if column_name not in preserve_order]))

    if "max_of_max" in column_names:  # ensure max of max is at the end
        column_names.remove("max_of_max")
        column_names = column_names + ["max_of_max"]

    if "file" in column_names:  # ensure max of max is at the end
        column_names.remove("file")
        preserve_order = ["file"] + preserve_order

    # takes data columns available for first item in list

    all_column_names = preserve_order + column_names

    if round_decimals:
        for datum in data:
            for k, v in datum.items():
                if isinstance(v, float):
                    datum[k] = round(v, 3)

    with open(output_file_path_no_extension + ".csv", "w", newline="") as csv_file:
        writer = DictWriter(csv_file, fieldnames=all_column_names)
        writer.writeheader()
        writer.writerows(data)


def construct_formatted_csv(
    data: List[Dict[str, any]],
    output_file_path_no_extension: str,
):
    log.info("Calling construct_formatted_csv")

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

    # get unique list of files (to be used as column headers)

    unique_files = list(set([datum["file"] for datum in data]))

    formatted_data = []
    for unique_node in unique_nodes:
        node_parameters_set = False
        file_maxima = []
        node_outputs = {
            "node_id": unique_node,
        }
        for i, unique_file in enumerate(unique_files):
            datum = seek_data(unique_node, unique_file)
            if datum is not None and datum["max_water_level"] is not None:
                file_maxima.append(datum["max_water_level"])
            if datum is not None:
                if not node_parameters_set:
                    for param in parameters_to_include:
                        node_outputs[param] = datum[param]
                    node_parameters_set = True
                node_outputs[unique_file] = datum["max_water_level"]
        node_outputs["max_of_max"] = max(file_maxima) if file_maxima else None
        formatted_data.append(
            node_outputs
        )

    construct_csv(
        formatted_data,
        output_file_path_no_extension,
    )


def convert_coordinate(
    from_crs: Proj,
    to_crs: Proj,
    x: float,
    y: float,
) -> (float, float):
    log.debug("Calling convert_coordinate")
    return transform(from_crs, to_crs, x, y)


def construct_geojson(from_crs: str, nodes: List[Dict[str, any]]) -> Dict[str, any]:
    log.info("Calling construct_geojson")

    geojson = {
        "type": "FeatureCollection",
        "features": []
    }

    from_crs = Proj('epsg:27200', preserve_units=False)
    to_crs = Proj('epsg:4326', preserve_units=False)

    for node in nodes:
        long, lat = convert_coordinate(from_crs, to_crs, node["x"], node["y"])
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


def convert_geojson_to_shp(geojson: Dict[str, any]):
    log.info("Calling convert_geojson_to_shp")
    return None


if __name__ == "__main__":
    pass
