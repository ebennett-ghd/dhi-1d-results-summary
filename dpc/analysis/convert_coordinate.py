#!
# -*- coding: utf-8 -*-
"""
╔═╗╦ ╦╔╦╗  ╔╦╗┬┌─┐┬┌┬┐┌─┐┬
║ ╦╠═╣ ║║   ║║││ ┬│ │ ├─┤│
╚═╝╩ ╩═╩╝  ═╩╝┴└─┘┴ ┴ ┴ ┴┴─┘

Created on 2021-12-04
@author: Edmund Bennett
@email: edmund.bennett@ghd.com
"""

from pyproj import Proj, transform

from dpc.utils.logger import logger as log


def convert_coordinate(
    from_crs: Proj,
    to_crs: Proj,
    x: float,
    y: float,
) -> (float, float):
    log.debug("Calling convert_coordinate")
    return transform(from_crs, to_crs, x, y)


if __name__ == "__main__":
    pass
