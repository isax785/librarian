import json
import os
CWD = os.path.dirname(__file__)


# External and Local absolute paths
EXT_PATH = "" 
LOCAL_PATH = ""

class Librarian:
    def __init__(self, ext_path:str=None, local_path:str=None):
        """
        - ext_path: str, external folder absolute path
        """
        self.ext_path = EXT_PATH if not ext_path else ext_path

    def build_index(self, folder_path):
        pass
        
    def compare_indexes(self):
        pass

    def update_local(self):
        pass

    def copy_file(self, local_filepath, ext_filepath):
        pass

    def delete_file(self, local_filepath):
        pass

    def update_file(self, local_filepath, ext_filepath):
        # TODO: same as self.copy_file() ?
        pass