#!
# -*- coding: utf-8 -*-
"""
╔═╗╦ ╦╔╦╗  ╔╦╗┬┌─┐┬┌┬┐┌─┐┬
║ ╦╠═╣ ║║   ║║││ ┬│ │ ├─┤│
╚═╝╩ ╩═╩╝  ═╩╝┴└─┘┴ ┴ ┴ ┴┴─┘

Created on 2021-10-22
@author: Edmund Bennett
@email: edmund.bennett@ghd.com
"""

from os.path import join, isfile
from os import walk
import re


class FileManipulation:
    """

    """
    FILE_BACKUP = r'~$'

    @staticmethod
    def get_files_recursively(directory, file_extension_allow_list=None, exclude_filename_text=None, filename_regex=None):
        """
        """
        file_paths = []
        if isfile(directory):
            file_paths.append(directory)
        else:
            for root, dirs, files in walk(directory, topdown=True):
                for name in files:
                    if name[:2] != FileManipulation.FILE_BACKUP:
                        if filename_regex is None:
                            if file_extension_allow_list is None:
                                if (exclude_filename_text is None) or (exclude_filename_text is not None) and (exclude_filename_text not in name):
                                    file_paths.append(join(root, name))
                            else:
                                if name.split('.')[-1].lower() in file_extension_allow_list:
                                    if (exclude_filename_text is None) or (exclude_filename_text is not None) and (exclude_filename_text not in name):
                                        file_paths.append(join(root, name))
                        else:
                            search = re.search(filename_regex, name)
                            if search is not None:
                                if file_extension_allow_list is None:
                                    if (exclude_filename_text is None) or ((exclude_filename_text is not None) and (exclude_filename_text not in name)):
                                        file_paths.append(join(root, name))
                                else:
                                    if name.split('.')[-1].lower() in file_extension_allow_list:
                                        if (exclude_filename_text is None) or ((exclude_filename_text is not None) and (exclude_filename_text not in name)):
                                            file_paths.append(join(root, name))

        return file_paths


if __name__ == "__main__":
    pass
