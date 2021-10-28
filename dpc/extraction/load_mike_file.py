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

from typing import Tuple
from dpc.utils.logger import logger as log

from DHI.Mike1D.ResultDataAccess import (
    ResultData,
    ResultDataSearch,
)
from DHI.Mike1D.Generic import Diagnostics, Connection


def load_file(file_path: str) -> Tuple[ResultData, ResultDataSearch]:
    log_entry = f"Loading file: {file_path}"
    log.info(log_entry)
    resultData = ResultData()
    resultData.Connection = Connection.Create(file_path)
    resultData.Load(Diagnostics(log_entry))
    searcher = ResultDataSearch(resultData)  # searcher helps to find reaches, nodes and catchments
    return resultData, searcher


if __name__ == "__main__":
    pass
