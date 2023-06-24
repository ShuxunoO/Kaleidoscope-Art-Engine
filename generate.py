from src.utils import file_operations as fio
from src.CONST_ENV import ENV_PATH as ENV
from src.utils import blend
from src.utils import pre_processing
import time
from pathlib import Path
# TODO:
# 1. 要先把之前生成的文件清空
import os

folder_path = "path/to/folder"  # 替换为您要删除文件的文件夹路径
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    os.remove(file_path)

if __name__ == "__main__":
    pre_processing.process()
    CONFIG = fio.load_json(ENV.CONFIG_PATH)
    layers_config = CONFIG["layerConfigurations"]
    layersInfo_recipe = fio.load_json(ENV.INFO_PATH.joinpath("layersInfo_recipe.json"))

    start_time = time.time()
    blend.setup_images(layers_config, layersInfo_recipe)
    print(f"Time cost: {time.time() - start_time:.2f}s")

