import json
import os
from pathlib import Path
import shutil

CWD = os.path.dirname(__file__)

# External and Local absolute paths
EXT_PATH = "." 
LOCAL_PATH = CWD

class Librarian:
    def __init__(self, ext_path:str=None, local_path:str=None, update:bool=False):
        """
        - ext_path: str, external folder path, absolute or relative
        - local_path: str, internal folder path, absolute or relative
        - update: bool, directly updates the 
        """
        self.ext_path = EXT_PATH if not ext_path else ext_path
        self.ext_path_abs = Path(self.ext_path).resolve()
        if not os.path.exists(self.ext_path_abs):
            raise ValueError(f"Folder {self.ext_path} does not exists!")
        self.local_path = LOCAL_PATH if not local_path else local_path
        self.local_path_abs = Path(self.local_path).resolve()
        if not os.path.exists(self.local_path_abs):
            os.makedirs(self.local_path_abs, exist_ok=True)
            print(f"Local path created: {self.local_path_abs}")
        self.ext_file_info = self.collect_file_info(self.ext_path)
        self.local_file_info = self.collect_file_info(self.local_path)

        self.compare_folders()
        if update:
            self.update_local_folder()

    def collect_file_info(self, folder_path):
        """
        Collect all the file relative paths and their information into a dicitonary: {rel_path: (info})}
        """
        folder = Path(folder_path).resolve()  # makes the path absolute
        all_files = [Path(root) / f for root, _, files in os.walk(folder) for f in files]
        file_info = {}
        for f in all_files:
            stat = f.stat()
            info = (stat.st_size, stat.st_mtime)
            if info:
                rel = f.relative_to(folder)
                file_info[rel] = info
        return file_info
        
    def compare_folders(self):
        self.added, self.deleted, self.modified = set(), set(), set()

        ext_files = set(self.ext_file_info.keys())
        local_files = set(self.local_file_info.keys())

        self.added = ext_files - local_files
        self.deleted = local_files - ext_files

        for f in ext_files and local_files:
            ext_size, ext_mtime = self.ext_file_info[f]
            local_size, local_mtime = self.local_file_info[f]
            if ext_size != local_size or abs(local_mtime - ext_mtime) > 1:
                self.modified.add(f)

    def update_local_folder(self):
        self.log = []
        print("--- Adding Files ---")
        for f in self.added:
            ext_file, local_file = self.ext_path / f, self.local_path / f
            local_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ext_file, local_file)
            print(f"  {f}")
            self.log.append(f"A - {f}")

        print("--- Deleting Files ---")
        for f in self.deleted:
            local_file = self.local_path
            if local_file.exists():
                local_file.unlink()
                print(f"  {f}")
                self.log.append(f"D - {f}")

        print("--- Modifying Files ---")
        for f in self.modified:
            ext_file, local_file = self.ext_path / f, self.local_path / f
            local_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ext_file, local_file)
            print(f"  {f}")
            self.log.append(f"M - {f}")

        print("--> Completed!!")

if __name__ == "__main__":
    pass