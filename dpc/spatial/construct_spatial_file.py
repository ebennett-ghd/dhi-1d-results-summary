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
):
    log.info("Calling construct_csv")
    column_names = list(data[0].keys())  # takes data columns available for first item in list

    with open(output_file_path_no_extension + ".csv", "w") as csv_file:
        writer = DictWriter(csv_file, fieldnames=column_names)
        writer.writeheader()
        writer.writerows(data)


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
                    "invert_levels": node["invert_levels"],
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
