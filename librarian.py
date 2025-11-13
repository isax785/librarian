import json
import os
from pathlib import Path
import shutil
import fnmatch

CWD = os.path.dirname(__file__)

LOCAL_PATH = CWD   # Local absolute path
LIBIGNORE_FILEPATH = os.path.join(CWD, ".libignore")

if not os.path.exists(LIBIGNORE_FILEPATH):
    with open(LIBIGNORE_FILEPATH, 'w') as f:
        f.write('')

class Librarian:
    def __init__(self, ext_path:str=None, local_path:str=None, update:bool=False, log:bool=False, ext_folder_skip:list[str]=[],  ext_file_skip:list[str]=[], local_folder_skip:list[str]=[], local_file_skip:list[str]=[], libignore_filepath:str=LIBIGNORE_FILEPATH, filtering:bool=False):
        """
        - ext_path: str, default=None, external folder path, absolute or relative
        - local_path: str, default=None, internal folder path, absolute or relative
        - update: bool, default=False, directly updates the local folder content
        - log: bool, default=False, save update log into a text file

        - ext_folder_skip: str, default=[], strings to skip external folders
        - ext_file_skip: str, default=[], strings to skip external files

        - local_folder_skip: str, default=[], strings to skip local folders
        - local_file_skip: str, default=[], strings to skip local files

        - libignore_filepath: str, default=LIBIGNORE_FILEPATH, the path of .libignore file
        - filtering: bool, default=True, uses the .libignore as it is intended, i.e. by excluding files/folders. If False, .libignore files/folders that should be excluded, will be the only ones to be transferred.
        """
        if not ext_path:
            raise AttributeError("Provide an external folder path, varname ext_path!!")
        self.ext_path = ext_path
        self.ext_path_abs = Path(self.ext_path).resolve()
        if not os.path.exists(self.ext_path_abs):
            raise ValueError(f"Folder {self.ext_path} does not exists!")
        self.local_path = LOCAL_PATH if not local_path else local_path
        self.local_path_abs = Path(self.local_path).resolve()
        if not os.path.exists(self.local_path_abs):
            os.makedirs(self.local_path_abs, exist_ok=True)
            print(f"Local path created: {self.local_path_abs}")    

        self.filtering = filtering  
        
        self.load_parse_libignore(libignore_filepath)
        self.update_folder_content()
        self.compare_folders()
        if update:
            self.update_local_folder(ext_folder_skip=ext_folder_skip,
                                     ext_file_skip=ext_file_skip, local_folder_skip=local_folder_skip,
                                     local_file_skip=local_file_skip, 
                                     filtering=filtering,
                                     log=log)

    def update_folder_content(self):
        try:
            print("Scanning EXTERNAL folder ... ", end="")
            self.ext_file_info = self.collect_file_info(self.ext_path)
            print("done!")
            print("Scanning LOCAL folder ... ", end="")
            self.local_file_info = self.collect_file_info(self.local_path)
            print("done!")
        except Exception as e:
            print(f"\n{str(e)}")

    def collect_file_info(self, folder_path):
        """
        Collect all the file relative paths and their information into a dicitonary structured as: {rel_path: (info})}
        """
        file_info = {}
        folder = Path(folder_path).resolve()  # makes the path absolute
        all_files = [Path(root) / f for root, _, files in os.walk(folder) for f in files]
        for f in all_files:
            stat = f.stat()
            info = (stat.st_size, stat.st_mtime)
            if info:
                rel = f.relative_to(folder)
                file_info[rel] = info
        return file_info
        
    def compare_folders(self):
        try:
            print("Comparing folders ... ", end="")
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
            print("done!")
        except Exception as e:
            print(f"\n{str(e)}")

    def load_parse_libignore(self, libignore_filepath=LIBIGNORE_FILEPATH):
        self.filters = []
        if not os.path.exists(libignore_filepath):
            print(".libignore file not provided. No filters will be applied.")
            return
        
        with open(libignore_filepath, 'r', encoding='utf-8') as f:
            self.libignore = f.read()
        for line in self.libignore:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            negated = line.startswith('!')
            if negated:
                line = line[1:]
            self.filters.append((line, negated))

    @staticmethod
    def check_skip(skip, path):
        " check if the path is to be skipped "
        return any([s in path.__str__() for s in skip])
    
    def is_ignored(self, path:str, base_dir:str):
        ignored = False
        for filter, negated in self.filters:
            if self.match_pattern(path, filter, base_dir):
                ignored = not negated
        if self.filtering:
            # TODO: check!
            ignored = not ignored
        return ignored
    
    def match_pattern(path, pattern, base_dir):
        " Match a path to a .gitignore-style pattern. "
        # Normalize
        path = path.replace(os.sep, '/')
        base_dir = base_dir.replace(os.sep, '/')
        pattern = pattern.replace(os.sep, '/')

        # If pattern starts with '/', it's relative to the base directory
        if pattern.startswith('/'):
            pattern = pattern[1:]
            path_rel = os.path.relpath(path, base_dir).replace(os.sep, '/')
        else:
            path_rel = path

        # Convert ** to */*/ and handle directory endings
        if pattern.endswith('/'):
            pattern = pattern.rstrip('/') + '/**'

        # Convert gitignore wildcards to fnmatch wildcards
        # Git ** matches across directories
        pattern = pattern.replace('**', '*')

        return fnmatch.fnmatch(path_rel, pattern)

    def update_local_folder(self, ext_folder_skip:list[str]=[],  ext_file_skip:list[str]=[], local_folder_skip:list[str]=[], local_file_skip:list[str]=[], filtering:bool=None, log:bool=False):

        self.filtering = filtering if filtering else self.filtering
        if not os.path.exists(self.local_path_abs):
            os.makedirs(self.local_path_abs, exist_ok=True)
            print(f"Local path created: {self.local_path_abs}")

        self.log_done, self.log_failed = [], []

        print("--- Adding Files ---")
        for f in self.added:
            if all([not self.check_skip(ext_folder_skip, f.parent),
                     not self.check_skip(ext_file_skip, f.name)]):
                try:
                    ext_file, local_file = self.ext_path / f, self.local_path / f
                    local_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(ext_file, local_file)
                    print(f"  {f}")
                    self.log_done.append(f"A - {f}")
                except Exception as e:
                    self.log_failed.append(f"A : {str(e)} - {f}")

        print("--- Deleting Files ---")
        for f in self.deleted:
            if all([not self.check_skip(local_folder_skip, f.parent.name),
                    not self.check_skip(local_file_skip, f.name)]):
                try:
                    local_file = self.local_path
                    if f.exists():
                        f.unlink()
                        print(f"  {f}")
                        self.log_done.append(f"D - {f}")
                except Exception as e:
                    self.log_failed.append(f"D : {str(e)} - {f}")

        print("--- Modifying Files ---")
        for f in self.modified:
            if all([not self.check_skip(local_folder_skip, f.parent.name),
                    not self.check_skip(local_file_skip, f.name)]):
                try:
                    ext_file, local_file = self.ext_path / f, self.local_path / f
                    local_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(ext_file, local_file)
                    print(f"  {f}")
                    self.log_done.append(f"M - {f}")
                except Exception as e:
                    self.log_failed.append(f"M : {str(e)} - {f}")

        print("--> Completed!!")

        if log:
            self.save_log()
            print("Log saved!")

    def save_log(self):
        with open(os.path.join(self.local_path, 'log.txt'), "w", encoding="utf-8") as logfile:
            logfile.write("--- TRANSFERS ---\n\n")
            logfile.write('\n'.join(self.log_done))
            logfile.write("\n\n--- ERRORS ---\n\n")
            logfile.write('\n'.join(self.log_failed))

if __name__ == "__main__":
    EXT_FOLDER = "external/folder/here"
    LOCAL_FOLDER = "."
    ext_folder_skip = []     # fill with strings for skip
    ext_file_skip = []       # fill with strings for skip 
    local_folder_skip = []   # fill with strings for skip
    local_file_skip = []     # fill with strings for skip
    local_file_skip = [] + [os.path.basename(__file__)]
    librarian = Librarian(ext_path=EXT_FOLDER, 
                      local_path=LOCAL_FOLDER,
                      ext_file_skip=ext_file_skip,
                      ext_folder_skip=ext_folder_skip,
                      local_folder_skip=local_folder_skip,
                      local_file_skip=local_file_skip,
                      update=True,
                      log=True)