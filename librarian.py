import json
import os
CWD = os.path.dirname(__file__)
JSON_FILEPATH = os.path.join(CWD, "settings.json")
with open(JSON_FILEPATH, 'r') as f:
    SETTINGS = json.load(f)

# add to json:
# - "sha"
# - "repo copy path"

class Librarian:
    def __init__(self):
        self.read_settings()
        if not self.sha:
            self.clone_repo()
        
    def read_settings(self):
        self.sha = SETTINGS.get("sha")
        self.repo_abs_path = SETTINGS.get("repo-abs-path")

    def diff_repo(self):
        pass

    def clone_repo(self):
        pass

    def copy_file(self):
        pass

    def update_repo(self):
        pass