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

    BASE_PATH = Path(__file__).parent.parent
    LAYER_PATH = Path.joinpath(BASE_PATH,"layers")
    CONFIG_PATH = Path.joinpath(BASE_PATH, "config.json")
    INFO_PATH = make_dir(Path.joinpath(BASE_PATH, "infos"))
    BUILD_PATH = make_dir(Path.joinpath(BASE_PATH, "build"))
    IMAGES_PATH = make_dir(Path.joinpath(BUILD_PATH, "images"))
    JSON_PATH = make_dir(Path.joinpath(BUILD_PATH, "jsons"))


if __name__ == "__main__":
    print(ENV_PATH.BASE_PATH)
    print(ENV_PATH.LAYER_PATH)
    print(ENV_PATH.CONFIG_PATH)
    print(ENV_PATH.INFO_PATH)
    print(ENV_PATH.BUILD_PATH)
    print(ENV_PATH.IMAGES_PATH)
    print(ENV_PATH.JSON_PATH)