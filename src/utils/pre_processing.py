import os
import re
import sys
from pathlib import Path

sys.path.append(".")
import file_operations as fop

from src.CONST_ENV import ENV_PATH as ENV

# TODO: 
    # 1. 定义计算图层列表权重之和的函数
    # 2. 定义计算当前图层中子文件夹图层权重之和的参数

def count_weights_in_layer_list(layer_info) -> float:
    """count sum of weights in layer_list of the  layer_info.

    Args:
        layer_info (dict): the layer info of the layer_list

    Returns:
        float: sum of weights in layer_list of the  layer_info.

    """
    sum = 0.0
    layer_list = layer_info.get("layer_list")
    if len(layer_list) == 0:
        return 0.0
    else:
        for layer in layer_list:
            layer_name = re.split("[%#.]", layer)[0]
            layer = layer_info.get(layer_name)
            percentage = layer.get("percentage")
            if percentage is not None:
                sum += percentage
            else:
                continue
        return sum


def count_weights_in_subdir_list(layer_info) -> float:
    """count sum of weights in subdir_list of the  layer_info.

    Args:
        layer_info (dict): the layer info of the subdir_list

    Returns:
        float: sum of weights in subdir_list of the  layer_info.

    """
    sum = 0.0
    subdir_list = layer_info.get("sub_dir_list")
    if len(subdir_list) == 0:
        return 0.0
    else:
        for subdir in subdir_list:
            subdir_info = layer_info.get(subdir)
            sum += count_weights_in_layer_list(subdir_info)
        return sum



if __name__ == "__main__":
    layers_info = fop.load_json(ENV.INFO_PATH.joinpath("layersInfo.json"))
    config_info = fop.load_json(ENV.CONFIG_PATH)
    layer_configs = config_info.get("layerConfigurations")
    for index in range(len(layer_configs)):
        config_info_item = layer_configs[index]
        layers_info_item = layers_info[index]
        layers_order_list = config_info_item.get("layersOrder")
        for layer in layers_order_list:
            layer_name = layer["name"]
            target_layer = layers_info_item[layer_name]
            if len(target_layer.get("layer_list")) != 0:
                layer_list_weight = count_weights_in_layer_list(target_layer)
                print(f"layer_list_weight: {layer_list_weight}")
            if len(target_layer.get("sub_dir_list")) != 0:
                subdir_list_weight = count_weights_in_subdir_list(target_layer)
                print(f"subdir_list_weight: {subdir_list_weight}")