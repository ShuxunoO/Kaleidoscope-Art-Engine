from src.utils import file_operations as fop
from src.CONST_ENV import ENV_PATH as ENV




if __name__ == "__main__":
    CONFIG = fop.load_json(ENV.CONFIG_PATH)
    for layer_config in CONFIG["layerConfigurations"]:
        print(layer_config["layersOrder"])
