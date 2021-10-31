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

from mikeio1d.res1d import ResultData, Diagnostics, Connection

from dpc.utils.logger import logger as log


def load_file(file_path: str) -> ResultData:
    log_entry = f"Loading file: {file_path}"
    log.info(log_entry)
    resultData = ResultData()
    resultData.Connection = Connection.Create(file_path)
    resultData.Load(Diagnostics(log_entry))
    return resultData


if __name__ == "__main__":
    pass
