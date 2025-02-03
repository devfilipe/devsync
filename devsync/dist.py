import os
import shutil
import pathlib

def copy_directory(source_dir, dest_dir):
    """
    Copies the contents of source_dir to dest_dir using shutil.
    Files and subdirectories are copied only if they do not exist in the destination.
    """
    os.makedirs(dest_dir, exist_ok=True)
    for item in source_dir.iterdir():
        dest_item = pathlib.Path(dest_dir) / item.name
        if not dest_item.exists():
            if item.is_dir():
                shutil.copytree(item, dest_item)
                print(f"Copied directory {item} to {dest_item}")
            else:
                shutil.copy2(item, dest_item)
                print(f"Copied file {item} to {dest_item}")
        else:
            print(f"{dest_item} already exists; skipping.")

def dist():
    current_dir = pathlib.Path(__file__).parent

    # Copy scripts directory
    scripts_source = current_dir.parent / "dist/scripts/test_handler"
    scripts_dest = os.path.expanduser("~/devsync/scripts/test_handler")
    if scripts_source.exists():
        copy_directory(scripts_source, scripts_dest)
    else:
        print(f"Source scripts directory {scripts_source} does not exist.")

    # Copy conf directory
    conf_source = current_dir.parent / "dist/conf"
    conf_dest = os.path.expanduser("~/devsync/conf")
    if conf_source.exists():
        copy_directory(conf_source, conf_dest)
    else:
        print(f"Source conf directory {conf_source} does not exist.")

if __name__ == "__main__":
    dist()
