import logging
import os
import shutil
from typing import List, Union

log = logging.getLogger(__name__)


NEWFILES_DIR_NAME = "NEWFILES"
NESTED_DIR_DEPTH = 4


def collect_fit_files_to_export(path_to_garmin_device, path_to_files_to_export: str):
    log.debug(f"Looking for file for export to device in {path_to_files_to_export}")
    newfiles_path = _find_newfiles_sub_dir_in_path(
        name_of_dir=NEWFILES_DIR_NAME,
        path=path_to_garmin_device,
        depth=NESTED_DIR_DEPTH,
    )
    n_files_exported = 0
    if os.path.isdir(newfiles_path):
        log.debug(f"found export dir at: {newfiles_path}")
        if os.path.isdir(path_to_files_to_export):
            fits = [
                os.path.join(root, name)
                for root, files in os.walk(path_to_files_to_export)
                for name in files
                # Some devices generate file named .FIT, other .fit
                if name.lower().endswith(".fit")
            ]
        if fits:
            for fit in fits:
                file_name = os.path.basename(fit)
                target_file = os.path.join(newfiles_path, file_name)
                if not os.path.isfile(target_file):
                    shutil.copy(fit, target_file)
                    log.info(f"copied file: {target_file}")
                    n_files_exported += 1
            if n_files_exported == 0:
                log.info("No new file exported")
        else:
            log.debug(f"could not find files to export at {path_to_files_to_export}")
    else:
        log.warning(f"No directory named '{NEWFILES_DIR_NAME}' found in path {path_to_garmin_device}")
    return n_files_exported


# TODO: this is an copy from wkz/io/fit_collector.py, make it 1 function
def _find_newfiles_sub_dir_in_path(name_of_dir: str, path: str, depth: int = 3) -> Union[str, bool]:
    def _get_all_subfolders(paths: List[str]) -> List[str]:
        sub_dirs = []
        for path in paths:
            sub_dirs += [f for f in os.scandir(path) if f.is_dir()]
        return sub_dirs

    paths = [path]
    for _ in range(depth):
        sub_dirs = _get_all_subfolders(paths)
        for sub_dir in sub_dirs:
            if name_of_dir.lower() == sub_dir.name.lower():
                return sub_dir.path
        paths = sub_dirs
    # if this line is reach it means the dir was not found
    return False
