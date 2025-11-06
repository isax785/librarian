# File and Folder Management with Python

- [[#File and Folder Management with Python|File and Folder Management with Python]]
	- [[#File and Folder Management with Python#1. Copy a File|1. Copy a File]]
	- [[#File and Folder Management with Python#2. Delete a File|2. Delete a File]]
	- [[#File and Folder Management with Python#3. Check if a Folder is Empty and Remove It|3. Check if a Folder is Empty and Remove It]]

---

Here are the Python functions for some file system tasks, along with examples of how to use them:


## 1. Copy a File

The `shutil.copy2()` function is generally preferred for copying files as it attempts to preserve more metadata (like timestamp) than `shutil.copy()`.

```Python
import shutil
import os

def copy_file(source_path, destination_folder):
    """
    Copies a file from the source path to the destination folder.
    
    Args:
        source_path (str): The full path to the file to be copied.
        destination_folder (str): The path to the folder where the file will be copied.
    """
    try:
        # Check if the destination folder exists, create it if it doesn't
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
            print(f"Created destination folder: {destination_folder}")

        shutil.copy2(source_path, destination_folder)
        print(f"✅ Successfully copied '{os.path.basename(source_path)}' to '{destination_folder}'")
    except FileNotFoundError:
        print(f"❌ Error: Source file not found at {source_path}")
    except Exception as e:
        print(f"❌ An error occurred during copy: {e}")

# Example Usage (You'd need to replace these with actual paths)
# source_file = "/path/to/source/file.txt"
# dest_dir = "/path/to/destination/folder"
# copy_file(source_file, dest_dir)
```

---

## 2. Delete a File

The `os.remove()` function is used to delete a single file.



```Python
import os

def delete_file(file_path):
    """
    Deletes a file at the specified path.

    Args:
        file_path (str): The full path to the file to be deleted.
    """
    try:
        os.remove(file_path)
        print(f"✅ Successfully deleted file: {file_path}")
    except FileNotFoundError:
        print(f"❌ Error: File not found at {file_path}")
    except Exception as e:
        print(f"❌ An error occurred during deletion: {e}")

# Example Usage (You'd need to replace this with an actual path)
# file_to_delete = "/path/to/folder/file_to_remove.log"
# delete_file(file_to_delete)
```

---

## 3. Check if a Folder is Empty and Remove It

You can use `os.listdir()` to get a list of contents in a directory. If the list is empty, the folder is empty. The `os.rmdir()` function removes an **empty** directory.



```Python
import os

def remove_empty_folder(folder_path):
    """
    Checks if a folder is empty. If it is, the folder is removed.

    Args:
        folder_path (str): The path to the folder to check and potentially remove.
    """
    try:
        # os.listdir returns an empty list if the folder exists but is empty
        if not os.listdir(folder_path):
            os.rmdir(folder_path)
            print(f"✅ Folder is empty and successfully removed: {folder_path}")
            return True
        else:
            print(f"➡️ Folder is NOT empty. Not removed: {folder_path}")
            return False
    except FileNotFoundError:
        print(f"❌ Error: Folder not found at {folder_path}")
        return False
    except OSError as e:
        # os.rmdir will raise an OSError if the directory is not empty
        print(f"❌ Error removing folder: {e} (This usually means the folder was not empty.)")
        return False

# Example Usage (You'd need to replace this with an actual path)
# folder_to_check = "/path/to/a/test_folder"
# remove_empty_folder(folder_to_check)
```

**Note:** For removing a **non-empty** folder and all its contents, you would use `shutil.rmtree(folder_path)`. Be extremely careful when using `shutil.rmtree()` as it permanently deletes everything inside the folder.

Would you like me to show you how to set up a simple temporary environment to **test** these three functions safely?