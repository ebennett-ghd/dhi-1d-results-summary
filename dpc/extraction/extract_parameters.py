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
from mikeio1d.res1d import ResultData
from typing import Dict, Tuple, Callable

from dpc.utils.logger import logger as log


def get_data(data: ResultData) -> Tuple[Dict[str, any], str]:
    log.info("Calling get_data")
    all_node_data = {}

    node_x_coordinates = get_node_coordinates(data, "x")
    node_y_coordinates = get_node_coordinates(data, "y")
    node_invert_levels = get_node_invert_levels(data)
    projection = get_projection(data)
    max_water_levels = get_aggregated_water_levels(data, max)

    node_ids = set(  # construct list of nodes
        list(node_x_coordinates.keys())
    )

    for node_id in node_ids:
        all_node_data[node_id] = {
            "x": node_x_coordinates[node_id],
            "y": node_y_coordinates[node_id],
            "invert_level": node_invert_levels[node_id] if node_id in node_invert_levels.keys() else None,
            "max_water_level": max_water_levels[node_id] if node_id in max_water_levels.keys() else None,
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
        try:
            invert_levels[node.Id] = node.BottomLevel
        except:
            log.warning(f"Bottom level data not available for node: {node.Id}")
    return invert_levels


def get_aggregated_water_levels(
    data: ResultData,
    aggregator: Callable = None,
) -> Dict[str, any]:
    log.info("Calling get_node_invert_levels")
    max_water_level = {}
    nodes = list(data.Nodes)
    for node in nodes:
        data_sets = list(node.DataItems)
        for data_set in data_sets:
            if data_set.Quantity.Id in ["WaterLevel", "Water Level"]:
                data = list(data_set.TimeData)
                max_water_level[node.Id] = aggregator(data) if aggregator is not None else data
                break

    return max_water_level


if __name__ == "__main__":
    pass
