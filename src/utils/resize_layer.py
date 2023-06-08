import os
import sys

sys.path.append('.')
from PIL import Image

from src.CONST_ENV import ENV_PATH as ENV
from src.utils.logging_factory import LoggerFactory

logf = LoggerFactory()
logger = logf.setup_logger("exceptions", ENV.INFO_PATH.joinpath("exceptions.log"))


def resize_imgs(width, height):
    layer_base_path = ENV.LAYER_PATH
    for root, _, files in os.walk(layer_base_path):
        if len(files) == 0:
            continue
        else:
            for file in files:
                    file_path = os.path.join(root, file)
                    img = Image.open(file_path)
                    original_width, original_height = img.size
                    img = img.resize((width, height), Image.Resampling.LANCZOS)
                    img.save(file_path)
                    print(f"Resized {file} from {original_width}*{original_height} to {width}*{height}")
                    logger.info(f"Resized {file} from {original_width}*{original_height} to {width}*{height}")


if __name__ == "__main__":
    resize_imgs(1024, 1024)
    
