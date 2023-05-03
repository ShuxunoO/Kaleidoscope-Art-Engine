import os
import re
import sys
from pathlib import Path

sys.path.append(".")
import file_operations as fop

from src.CONST_ENV import ENV_PATH as ENV


def count_weights_in_layer_list(layer_info) -> tuple:
    """count sum of weights in layer_list of the  layer_info.

    Args:
        layer_info (dict): the layer info of the layer_list

    Returns:
        tuple: sum of weights in layer_list of the  layer_info and total number of layer with percentage.

    """
    weight_sum = 0.0
    layer_counter = 0
    layer_list = layer_info.get("layer_list")
    if len(layer_list) == 0:
        return 0.0
    else:
        for layer in layer_list:
            layer_name = re.split("[%#.]", layer)[0]
            layer = layer_info.get(layer_name)
            percentage = layer.get("percentage")
            if percentage is not None:
                weight_sum += percentage
                # 加入异常处理，如果图层的权重之和超过1，抛出异常
                layer_counter += 1
            else:
                continue
        return weight_sum, layer_counter


def count_weights_in_subdir_list(layer_info) -> tuple:
    """count sum of weights in subdir_list of the  layer_info.

    Args:
        layer_info (dict): the layer info of the subdir_list

    Returns:
        tuple: sum of weights in subdir_list of the layer_info and total number of layer with percentage.

    """
    weight_sum = 0.0
    layer_counter = 0
    subdir_list = layer_info.get("sub_dir_list")
    if len(subdir_list) == 0:
        return 0.0
    else:
        for subdir in subdir_list:
            subdir_info = layer_info.get(subdir)
            dir_weight, counter = count_weights_in_layer_list(subdir_info)
            weight_sum += dir_weight
            # 加入异常处理，如果图层的权重之和超过1，抛出异常
            layer_counter += counter
        return weight_sum, layer_counter


def update_layers_weight(rest_weight, rest_layer_num, layer_info) -> tuple:
    """
        update the weight of the layer_info.

    Args:
        rest_weight (float): the rest weight of the layer_info
        rest_layer_num (int): the rest layer number of the layer_info
        layer_info (dict): the layer info of the layer_info
        
    Returns:
        tuple: rest weight and rest layer number of the layer without percentage.

    """
    # 将剩余的权重赋予给剩余的图层
    layer_list = layer_info.get("layer_list")
    average_weight = round(rest_weight / rest_layer_num, 6)
    for layer in layer_list:
        layer_name = re.split("[%#.]", layer)[0]
        layer = layer_info.get(layer_name)
        if layer.get("percentage") is None:
            if rest_layer_num == 1:
                layer["percentage"] = round(rest_weight, 6)
            else:
                layer["percentage"] = average_weight
                rest_weight -= average_weight
                rest_layer_num -= 1
        else:
            continue

    return rest_weight, rest_layer_num

def balance_weights_in_layer_list(layer_info) -> None:
    """
        balance the weights in layer_list of the layer_info.

    Args:
        layer_info (dict): the layer info of the layer_list

    """
    weight_sum, layer_counter = count_weights_in_layer_list(layer_info)
    rest_weight = 1.0 - weight_sum
    rest_layer_num = layer_info.get("layers_number") - layer_counter
    # TODO :图层数为负数，抛出异常
    update_layers_weight(rest_weight, rest_layer_num, layer_info)


def balance_weights_in_subdir_list(layer_info) -> None:
    """ 
        balance the weights in subdir_list of the layer_info.

    Args:
        layer_info (dict): the layer info of the subdir_list
    """
    weight_sum, layer_counter = count_weights_in_subdir_list(layer_info)
    rest_weight = 1.0 - weight_sum
    rest_layer_num = layer_info.get("layers_number") - layer_counter
    # 图层数为负数，抛出异常
    for subdir in layer_info.get("sub_dir_list"):
        subdir_info = layer_info.get(subdir)
        rest_weight, rest_layer_num = update_layers_weight(rest_weight, rest_layer_num, subdir_info)

def register_layer_list_weight(layer_info) -> None:
    """
        register the weight of the layer_list in the layer_info.

    Args:
        layer_info (dict): the layer info of the layer_list

    """
    layer_list = layer_info.get("layer_list")
    # 登记图层列表中的图层权重
    if len(layer_list) != 0:
        for layer in layer_list:
            layer_name = re.split("[%#.]", layer)[0]
            layer_weight = layer_info.get(layer_name).get("percentage")
            layer_info["layer_weights_list"].append(layer_weight)


def register_subdir_list_weight(layer_info) -> None:
    """
        register the weight of the subdir_list in the layer_info.

    Args:
        layer_info (dict): the layer info of the subdir_list

    """
    sub_dir_list = layer_info.get("sub_dir_list")
    # 登记子文件夹列表中的图层权重
    if len(sub_dir_list) != 0:
        for subdir in sub_dir_list:
            subdir_info = layer_info.get(subdir)
            # 登记子文件夹中的图层权重
            register_layer_list_weight(subdir_info)
            sub_dir_weight = round(sum(subdir_info.get("layer_weights_list")), 6)
            # 登记该子文件夹的权重
            layer_info["subdir_weights_list"].append(sub_dir_weight)


def pre_operation(layer_info_dict) -> None:
    """
        pre operation before balance the weights in layer_info.

    Args:
        layer_info_dict (dict): the layer info of the layer_info

    """
    layers_info = layer_info_dict.get("layers_info")
    for layer_name, layer_info in layers_info.items():
        if len(layer_info.get("layer_list")) != 0:
            balance_weights_in_layer_list(layer_info)
            register_layer_list_weight(layer_info)
        if len(layer_info.get("sub_dir_list")) != 0:
            balance_weights_in_subdir_list(layer_info)
            register_subdir_list_weight(layer_info)



if __name__ == "__main__":
    layers_info = fop.load_json(ENV.INFO_PATH.joinpath("layersInfo.json"))
    for info_item in layers_info:
        pre_operation(info_item)

    fop.save_json(ENV.INFO_PATH,"layersInfo_update.json", layers_info)