#!
# -*- coding: utf-8 -*-
"""
╔═╗╦ ╦╔╦╗  ╔╦╗┬┌─┐┬┌┬┐┌─┐┬
║ ╦╠═╣ ║║   ║║││ ┬│ │ ├─┤│
╚═╝╩ ╩═╩╝  ═╩╝┴└─┘┴ ┴ ┴ ┴┴─┘

Created on 2020-12-18
@author: Edmund Bennett
@email: edmund.bennett@ghd.com
"""

import logging
import tempfile

from os.path import join
from logging.handlers import RotatingFileHandler

MAX_LENGTH = 10000


class WhitespaceRemovingFormatter(logging.Formatter):
    def format(self, record):
        record.msg = record.msg.strip()
        if len(record.msg) > MAX_LENGTH:
            record.msg = record.msg[:MAX_LENGTH] + "..."
        return super(WhitespaceRemovingFormatter, self).format(record)


logging.basicConfig(level=logging.INFO)
formatter = WhitespaceRemovingFormatter(
    "%(asctime)s.%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    "%Y-%m-%d %H:%M:%S",
)

tempdir = tempfile.gettempdir()
log_file_path = join(tempdir, "dpc.log")

log_file_path = RotatingFileHandler(
    log_file_path,
    maxBytes=10000000,
    backupCount=5,
)

log_file_path.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(log_file_path)


if __name__ == "__main__":
    pass
