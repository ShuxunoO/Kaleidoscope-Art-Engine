from src.utils import file_operations as fio
from src.CONST_ENV import ENV_PATH as ENV

# TODO:
# 1. 要先把之前生成的文件清空


if __name__ == "__main__":
    CONFIG = fio.load_json(ENV.CONFIG_PATH)
    for layer_config in CONFIG["layerConfigurations"]:
        print(layer_config["layersOrder"])
    