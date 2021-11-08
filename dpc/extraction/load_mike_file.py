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

from mikeio1d.res1d import ResultData, Diagnostics, Connection, Res1D

from dpc.utils.logger import logger as log


def load_prf_file(file_path: str) -> ResultData:
    log_entry = f"Loading file: {file_path}"
    log.info(log_entry)
    resultData = ResultData()
    resultData.Connection = Connection.Create(file_path)
    resultData.Load(Diagnostics(log_entry))
    return resultData


def load_res_file(file_path: str) -> ResultData:
    log.info(f"Loading file: {file_path}")
    resultData = Res1D(file_path)
    return resultData.read()


if __name__ == "__main__":
    pass
