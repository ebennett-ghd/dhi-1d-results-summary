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

import pandas as pd
from mikeio1d.res1d import ResultData
from typing import Dict, Tuple, Callable

from dpc.utils.logger import logger as log


def get_data(
    data: ResultData,
    df: pd.DataFrame = None,
    include_nodes: bool = True,
    include_reaches: bool = True,
) -> Tuple[Dict[str, any], str]:
    log.debug("Calling get_data")

    all_node_data = {}

    projection = get_projection(data)

    start_time, end_time, number_of_time_steps = get_timing_data(
        data,
    )

    node_x_coordinates = get_node_coordinates(
        data,
        "x",
        include_nodes=include_nodes,
        include_reaches=include_reaches,
    )
    node_y_coordinates = get_node_coordinates(
        data,
        "y",
        include_nodes=include_nodes,
        include_reaches=include_reaches,
    )
    node_invert_levels = get_node_invert_levels(
        data,
        df=df,
        include_nodes=include_nodes,
        include_reaches=include_reaches,
    )
    max_water_levels, max_water_level_timings = get_aggregated_water_levels(
        data,
        max,
        include_nodes=include_nodes,
        include_reaches=include_reaches,
        df=df,
    )

    node_ids = set(  # construct list of nodes
        list(node_x_coordinates.keys())
    )

    for node_id in node_ids:
        max_water_level = None
        if node_id in max_water_levels.keys():
            max_water_level = max_water_levels[node_id]
        else:
            tolerance = 0.1
            # TODO: match within a distance threshold down the reach

        max_water_level_timing = None
        if node_id in max_water_level_timings.keys():
            max_water_level_timing = max_water_level_timings[node_id]

        all_node_data[node_id] = {
            "x": node_x_coordinates[node_id],
            "y": node_y_coordinates[node_id],
            "invert_level": node_invert_levels[node_id] if node_id in node_invert_levels.keys() else None,
            "max_water_level": max_water_level,
            "max_water_level_timing": max_water_level_timing,
        }

    return all_node_data, projection


def get_projection(data: ResultData) -> str:
    log.debug("Calling get_projection")
    return data.ProjectionString


def get_timing_data(data: ResultData) -> Tuple[str, str, str]:
    return data.StartTime, data.EndTime, data.NumberOfTimeSteps


def get_node_coordinates(
    data: ResultData,
    coordinate: str,
    df: pd.DataFrame = None,
    include_nodes: bool = True,
    include_reaches: bool = True,
) -> Dict[str, float]:
    log.debug("Calling get_node_coordinates")
    coordinates = {}

    if hasattr(data, "Nodes") and include_nodes:
        nodes = list(data.Nodes)
        if df is None:
            log.debug(f"Attempting to take data direct from data structure")
            for node in nodes:
                coord = None
                if coordinate == "x":
                    coord = node.get_XCoordinate()
                elif coordinate == "y":
                    coord = node.get_YCoordinate()
                else:
                    log.error(f"Spatial coordinate not property specified. Got: {coordinate}")
                coordinates[node.Id] = coord
        else:
            log.debug(f"Attempting to take data from relevant reach via DataFrame")
            relevant_columns = [col for col in df.columns if "Water Level" in col or "WaterLevel" in col]
            for col in relevant_columns:
                node_id, chainage = col.split(":")[1:]
                node = [node for node in nodes if node.Id == f"{chainage} {node_id}"]
                if node:
                    matched_node = node[0]
                    grid_point_index = matched_node.Reaches[0].Reach.GridPointIndexForChainage(chainage)
                    coord = None
                    if coordinate == "x":
                        coord = list(matched_node.Reaches[0].Reach.GridPoints)[grid_point_index].get_X()
                    elif coordinate == "y":
                        coord = list(matched_node.Reaches[0].Reach.GridPoints)[grid_point_index].get_Y()
                    else:
                        log.error(f"Spatial coordinate not property specified. Got: {coordinate}")
                    chainage = round(chainage, 1) if "." in str(chainage) else f"{chainage}.0"
                    coordinates[f"{node_id} {chainage}"] = coord

    if hasattr(data, "Reaches") and include_reaches:
        reaches = list(data.Reaches)
        for reach in reaches:
            try:
                reach_id = reach.Id
                if "-" in reach_id:
                    reach_id = reach_id.split("-")[0]
                grid_points = list(reach.GridPoints)
                if grid_points:
                    for grid_point in grid_points:
                        if grid_point.get_PointType() in [2, 1025]:  # h-point is 1025, interpolated h-point is 2
                            chainage = grid_point.get_Chainage()
                            log.debug(f"get_node_coordinates - Reach: {reach_id} chainage: {grid_point.get_Chainage()} has point type: {grid_point.get_PointType()}")
                            chainage = round(chainage, 1) if "." in str(chainage) else f"{chainage}.0"
                            full_grid_point_id = f"{reach_id} {chainage}"
                            result = None
                            if coordinate == "x":
                                result = grid_point.X
                            elif coordinate == "y":
                                result = grid_point.Y
                            coordinates[full_grid_point_id] = result
            except:
                log.warning(f"Bottom level data not available for reach: {reach.Id}")

    return coordinates


def get_node_invert_levels(
    data: ResultData,
    df: pd.DataFrame,
    include_nodes: bool = True,
    include_reaches: bool = True,
) -> Dict[str, float]:
    log.debug("Calling get_node_invert_levels")
    invert_levels = {}

    if hasattr(data, "Nodes") and include_nodes:
        nodes = list(data.Nodes)
        if df is None:
            log.debug(f"Attempting to take data direct from data structure")
            for node in nodes:
                invert_levels[node.Id] = node.BottomLevel
        else:
            log.debug(f"Attempting to take data from relevant reach via DataFrame")
            relevant_columns = [col for col in df.columns if "Water Level" in col or "WaterLevel" in col]
            for col in relevant_columns:
                node_id, chainage = col.split(":")[1:]
                node = [node for node in nodes if node.Id == f"{node_id} {round(chainage, 0)}"]
                if node:
                    matched_node = node[0]
                    grid_point_index = matched_node.Reaches[0].Reach.GridPointIndexForChainage(chainage)
                    chainage = round(chainage, 1) if "." in str(chainage) else f"{chainage}.0"
                    invert_levels[f"{node_id} {chainage}"] = list(matched_node.Reaches[0].Reach.GridPoints)[grid_point_index].get_Z()

    if hasattr(data, "Reaches") and include_reaches:
        reaches = list(data.Reaches)
        for reach in reaches:
            try:
                reach_id = reach.Id
                if "-" in reach_id:
                    reach_id = reach_id.split("-")[0]
                grid_points = list(reach.GridPoints)
                if grid_points:
                    for grid_point in grid_points:
                        log.debug(f"get_node_invert_levels - Reach: {reach_id} chainage: {grid_point.get_Chainage()} has point type: {grid_point.get_PointType()}")
                        if grid_point.get_PointType() in [2, 1025]:  # h-point is 1025, interpolated h-point is 2
                            chainage = grid_point.get_Chainage()
                            chainage = round(chainage, 1) if "." in str(chainage) else f"{chainage}.0"
                            full_grid_point_id = f"{reach_id} {chainage}"
                            invert_levels[full_grid_point_id] = grid_point.Z
            except:
                log.warning(f"Bottom level data not available for reach: {reach.Id}")

    return invert_levels


def get_aggregated_water_levels(
    data: ResultData,
    aggregator: Callable = None,
    include_nodes: bool = True,
    include_reaches: bool = True,
    df: pd.DataFrame = None,
) -> Tuple[Dict[str, any], Dict[str, any]]:
    log.debug("Calling get_aggregated_water_levels")
    max_water_level = {}
    max_water_level_timings = {}

    if df is None:
        log.debug("Processing ResultData directly")
        if hasattr(data, "Nodes") and include_nodes:
            nodes = list(data.Nodes)
            for node in nodes:
                node_data_sets = list(node.DataItems)
                for node_data_set in node_data_sets:
                    if node_data_set.Quantity.Id in ["WaterLevel", "Water Level"]:
                        data = list(node_data_set.TimeData)
                        max_water_level[node.Id] = aggregator(data) if aggregator is not None else data
                        max_water_level_timings[node.Id] = None
                        if aggregator is not None:
                            max_water_level_timings[node.Id] = len(data) - 1 - data[::-1].index(max_water_level[node.Id])
                        break

        if hasattr(data, "Reaches") and include_reaches:
            reaches = list(data.Reaches)
            for reach in reaches:
                reach_data_sets = list(reach.DataItems)
                for reach_data_set in reach_data_sets:
                    if reach_data_set.Quantity.Id in ["WaterLevel", "Water Level"]:
                        element_data = []
                        for element_index in range(reach_data_set.NumberOfElements):
                            time_series_data = []
                            for x in range(reach_data_set.TimeData.NumberOfTimeSteps):
                                time_series_data.append(reach_data_set.TimeData.GetValue(x, element_index))
                            aggregated_time_series_data = aggregator(time_series_data) if aggregator is not None else time_series_data
                            element_data.append(aggregated_time_series_data)
                        max_water_level[reach.Id] = aggregator(element_data) if aggregator is not None else element_data
                        max_water_level_timings[reach.Id] = None
                        if aggregator is not None:
                            max_water_level_timings[reach.Id] = len(element_data) - 1 - element_data[::-1].index(max_water_level[reach.Id])
                        break

    else:
        log.debug("Processing DataFrame")
        relevant_columns = [col for col in df.columns if "Water Level" in col or "WaterLevel" in col]
        relevant_df = df[relevant_columns]
        for col in relevant_df.columns:
            node_id, chainage = col.split(":")[1:]
            water_level_time_series = df[col].to_list()
            if "." in str(chainage):
                if chainage[-1] == "5":  # addresses python incorrect rounding cases
                    chainage = round(float(chainage) + 0.01, 1)
                else:
                    chainage = round(float(chainage), 1)
            else:
                chainage = f"{chainage}.0"
            max_water_level_time_series = max(water_level_time_series)
            max_water_level[f"{node_id} {chainage}"] = max_water_level_time_series
            max_water_level_timings[f"{node_id} {chainage}"] = len(water_level_time_series) - 1 - water_level_time_series[::-1].index(max_water_level_time_series)

    return max_water_level, max_water_level_timings


if __name__ == "__main__":
    pass
