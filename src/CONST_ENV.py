import os
import json
from pathlib import Path


class ENV_PATH:
    """
    Description: Path class for the project
    
    """
    def make_dir(file_path):
        """
            if the file path does not exist, create it

        Args:
            file_path (str / pathlib.Path obj): the path to a file

        Returns:
            _type_: the path to the file
        """

        if not Path(file_path).exists():
            Path.mkdir(file_path)
        return file_path

    BASE_PATH = Path("CONST_ENV.py").absolute().parent
    LAYER_PATH = Path.joinpath(BASE_PATH,"layers")
    CONFIG_PATH = Path.joinpath(BASE_PATH, "configs", "config.json")
    INFO_PATH = make_dir(Path.joinpath(BASE_PATH, "infos"))
    LOGGING_PATH = INFO_PATH
    OUTPUT_PATH = make_dir(Path.joinpath(BASE_PATH, "output"))
    IMAGES_PATH = make_dir(Path.joinpath(OUTPUT_PATH, "images"))
    JSON_PATH = make_dir(Path.joinpath(OUTPUT_PATH, "jsons"))