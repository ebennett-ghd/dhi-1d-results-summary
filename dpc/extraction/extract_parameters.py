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

import mikeio1d
from DHI.Mike1D.ResultDataAccess import ResultData
from typing import Dict, Tuple

from dpc.utils.logger import logger as log


def get_data(data: ResultData) -> Tuple[Dict[str, any], str]:
    log.info("Calling get_data")
    all_node_data = {}

    node_x_coordinates = get_node_coordinates(data, "x")
    node_y_coordinates = get_node_coordinates(data, "y")
    node_invert_levels = get_node_invert_levels(data)
    projection = get_projection(data)

    node_ids = set(  # construct list of nodes
        list(node_invert_levels.keys())
    )

    for node_id in node_ids:
        all_node_data[node_id] = {
            "x": node_x_coordinates[node_id],
            "y": node_y_coordinates[node_id],
            "invert_levels": node_invert_levels[node_id],
        }

    return all_node_data, projection


def get_projection(data: ResultData) -> str:
    log.info("Calling get_projection")
    return data.ProjectionString


def get_node_coordinates(data: ResultData, coordinate: str) -> Dict[str, float]:
    log.info("Calling get_node_coordinates")
    coordinates = {}
    nodes = list(data.Nodes)
    for node in nodes:
        coord = None
        if coordinate == "x":
            coord = node.get_XCoordinate()
        elif coordinate == "y":
            coord = node.get_XCoordinate()
        else:
            log.critical(f"Spatial coordinate not property specified. Got: {coordinate}")
        coordinates[node.Id] = coord
    return coordinates


def get_node_invert_levels(data: ResultData) -> Dict[str, float]:
    log.info("Calling get_node_invert_levels")
    invert_levels = {}
    nodes = list(data.Nodes)
    for node in nodes:
        invert_levels[node.Id] = node.BottomLevel
    return invert_levels



if __name__ == "__main__":
    pass
