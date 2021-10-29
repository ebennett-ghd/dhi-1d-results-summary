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

from typing import List, Dict, Callable

from dpc.utils.logger import logger as log


def extract_extremum(
    data: List[Dict[str, any]],
    data_parameter: str,
    aggregation_function: Callable,
) -> Dict[str, any]:
    """
    Extract extremum of indicated parameter from data
    :param data: data payload
    :param data_parameter: parameter for which to determine extremum
    :param aggregation_function: function to use to aggregate data i.e. max
    :return: datum for which indicated parameter is aggregated
    """
    max_parameter = aggregation_function([v for datum in data for k, v in datum.items() if k == data_parameter])
    max_datum = [datum for datum in data if datum[data_parameter] == max_parameter][0]
    return max_datum


def extract_extrema(
    data: List[Dict[str, any]],
    data_parameter: str,
    aggregation_function: Callable,
    group_by_parameter: str = None,
) -> List[Dict[str, any]]:
    """
    Extract extrema of indicated parameter from data
    :param aggregation_function:
    :param data: data payload
    :param data_parameter: parameter for which to determine extrema
    :param group_by_parameter: optional grouping parameter
    :return: data for which indicated parameter is aggregated
    """
    log.info("Calling extract_max_of_max")
    assert data_parameter in data[0].keys(), "Data parameter must be a column of the input data"
    if group_by_parameter is not None:
        assert group_by_parameter in data[0].keys(), "Group by parameter must be a column of the input data"
        groupings = set([datum[group_by_parameter] for datum in data])
        grouped_maxima = []
        for grouping in groupings:
            this_group = [datum for datum in data if datum[group_by_parameter] == grouping]
            max_datum = extract_extremum(this_group, data_parameter, aggregation_function)
            grouped_maxima.append(max_datum)
        return grouped_maxima
    else:
        return [extract_extremum(data, data_parameter, aggregation_function)]


if __name__ == "__main__":
    pass
