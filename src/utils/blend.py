import copy
import hashlib
import random
import sys
from datetime import datetime
from pathlib import Path
sys.path.append(".")
import file_operations as fop
from PIL import Image
from src.CONST_ENV import ENV_PATH as ENV

from src.utils import pre_processing 

if __name__ == "__main__":
    pre_processing.process()
    CONFIG = fop.load_json(ENV.CONFIG_PATH)
    layersInfo_recipe = fop.load_json(ENV.INFO_PATH.joinpath("layersInfo_recipe.json"))


    elements = [
                            "Blue_Green",
                            "Blue_Purple",
                            "Blue_Yellow",
                            "Dark_Blue",
                            "Ice_Blue",
                            "Lightblue_Purple",
                            "Light_Blue",
                            "Purple_Blue",
                            "White_Blue"
                        ]

    probabilities = [
                            0.111111,
                            0.111111,
                            0.111111,
                            0.111111,
                            0.111111,
                            0.111111,
                            0.111111,
                            0.111111,
                            0.111112
                        ]
    for _ in range(100):
        layer = random.choices(elements, probabilities)
        print(layer)