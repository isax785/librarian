import os
import hashlib
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_file_info(path):
    """Return (size, mtime, hash) for a file, lazily computing hash only when needed."""
    try:
        stat = path.stat()
        return (stat.st_size, stat.st_mtime, None)
    except FileNotFoundError:
        return None

def compute_hash(path):
    """Compute MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def scan_folder(folder, use_hash=False, max_workers=8):
    """Scan folder contents efficiently with optional parallel hashing."""
    folder = Path(folder).resolve()
    file_info = {}

    # Step 1: Collect all files and metadata
    all_files = [Path(root) / f for root, _, files in os.walk(folder) for f in files]
    for f in all_files:
        info = get_file_info(f)
        if info:
            rel = f.relative_to(folder)
            file_info[str(rel)] = info

    # Step 2: Optionally compute hashes in parallel
    if use_hash:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_path = {executor.submit(compute_hash, folder / rel): rel for rel in file_info.keys()}
            for future in as_completed(future_to_path):
                rel = future_to_path[future]
                try:
                    hash_val = future.result()
                    size, mtime, _ = file_info[rel]
                    file_info[rel] = (size, mtime, hash_val)
                except Exception as e:
                    print(f"Error hashing {rel}: {e}")
    return file_info

def compare_folders(src_info, dst_info, use_hash=False):
    added, deleted, modified = set(), set(), set()

    src_files = set(src_info.keys())
    dst_files = set(dst_info.keys())

    added = src_files - dst_files
    deleted = dst_files - src_files

    # Compare common files
    for f in src_files & dst_files:
        s_size, s_mtime, s_hash = src_info[f]
        d_size, d_mtime, d_hash = dst_info[f]

        if s_size != d_size or abs(s_mtime - d_mtime) > 1:
            modified.add(f)
        elif use_hash and s_hash != d_hash:
            modified.add(f)
    return added, deleted, modified

def sync_folders(src, dst, added, deleted, modified):
    src, dst = Path(src), Path(dst)

    for f in added:
        src_file, dst_file = src / f, dst / f
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)
        print(f"Added: {f}")

    for f in deleted:
        dst_file = dst / f
        if dst_file.exists():
            dst_file.unlink()
            print(f"Deleted: {f}")

    for f in modified:
        src_file, dst_file = src / f, dst / f
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)
        print(f"Updated: {f}")

def main():
    src = input("Source folder: ").strip()
    dst = input("Destination folder: ").strip()
    use_hash = input("Use hashing for full accuracy? [y/N]: ").strip().lower() == 'y'

    print("Scanning folders...")
    src_info = scan_folder(src, use_hash=use_hash)
    dst_info = scan_folder(dst, use_hash=use_hash)

    added, deleted, modified = compare_folders(src_info, dst_info, use_hash=use_hash)

    print("\n=== Results ===")
    print(f"Added: {len(added)}, Deleted: {len(deleted)}, Modified: {len(modified)}")

    if input("\nSync destination to match source? [y/N]: ").strip().lower() == "y":
        sync_folders(src, dst, added, deleted, modified)

if __name__ == "__main__":
    main()