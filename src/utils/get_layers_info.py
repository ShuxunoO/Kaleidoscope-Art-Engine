import re
import sys
from pathlib import Path
sys.path.append(".")  # add the current path to the system path
from src.CONST_ENV import ENV_PATH as ENV


def get_dirlist_and_filelist(file_path):
    """
    It takes a file path and returns a files list and a subfolders list in the path
    :param file_path: the path to the folder containing the files and subfolders
    :return: A file list and a subfolders list.
    """

    # find all files in the file_path
    file_list = Path.iterdir(file_path)

    # pick out subfolders in file_path
    dir_list = [f.stem for f in file_path.iterdir() if f.is_dir()]

    # get the remaining files in file_path
    layer_list = list(set(file_list) - set(dir_list))

    return layer_list, dir_list


def get_layers_info(base_path, layer_info):
    """
        It takes a file name and a base path, and returns a dictionary, which contains the
        file name as it's key and the layerinfo dictionary of it's value.

        :param base_path: the path to the folder containing the file
        :param layer_name: the name of the file you want to get the layerinfo from
    """
    # get the file list and subfolder list in the base path
    current_path = Path.joinpath(base_path, layer_info["name"])
    layer_list, dir_list = get_dirlist_and_filelist(current_path)

    # a dictionary to store the layers infomation in base path
    layerinfo_dict = {}
    layerinfo_dict.update(layer_info)
    layerinfo_dict.update({
        # remove the suffix and weight to get purename
        "layer_list": [re.split("[#%.]", layer)[0] for layer in layer_list],
        "dir_list": dir_list,
        "beacon_dir_list":[],
        "subordinate_dir_list":[],
        "layers_number": get_file_num(current_path),
        "sum_of_weights": "unknown",
        "is_balanced": False
        })


    if len(layer_list):
        get_layerinfo_in_currentdir(current_path, layer_list, layerinfo_dict)

    if len(dir_list):
        get_layerinfo_in_subdir(
            layer_info["name"], current_path, layerinfo_dict)

    return {layer_info["name"]: layerinfo_dict}


def get_layerinfo_in_currentdir(file_path, layer_name, layerinfo_dict):
    """
    This function takes a base path and a file name, and returns a dictionary with the layer name as
    the key and a dictionary of layer information as the value
    When "existSubdir" is False, it means there is no subdirectory in current base path.

    :param base_path: The path to the folder where the layer is stored
    :param file_name: The name of the layer
    :return: A dictionary with the layer name as the key and the layer infos as the value.
    """
    layer_list, dir_list = get_dirlist_and_filelist(file_path)
    for layer in layer_list:
        item_name = layer[:-4]  # remove the suffix
        name, percentage, weight = get_purename_and_weight(item_name)
        layer_info = {
            "path": str(Path(file_path.joinpath(layer)).resolve()),
            "percentage": percentage,
            "weight": weight
        }
        layerinfo_dict.update({name: layer_info})


def get_layerinfo_in_subdir(dir_name, base_path, layerinfo_dict):
    """
    It takes a base path and a directory name, and returns a dictionary, which contains the
    dirctory name as it's key and the layerinfo dictionary of it's value.
    When "existSubdir" is True, it means there existing subdirectory in current base path.

    :param base_path: the path of the directory where the subdirectories are located
    :param layerinfo_dict: a dictionary to store the information
    """
    layer_list, dir_list = get_dirlist_and_filelist(base_path)
    for dir_item in dir_list:
        sub_path = Path(base_path.joinpath(dir_item)).resolve()
        sublayer_list = os.listdir(sub_path)
        sublayer_info_dict = {}
        sublayer_info_dict.update({"name": dir_name + "-" + dir_item,
                                "layers_number": len(os.listdir(sub_path)),
                                    })
        sublayer_info_dict.update(
            {"layer_list": [re.split("[#%.]", layer)[0] for layer in os.listdir(sub_path)]})
        for layer in sublayer_list:
            layer_name = layer[:-4]  # remove the suffix
            name, weight = get_purename_and_weight(layer_name)
            sublayer_info_dict.update({name: {
                "path": str(sub_path.joinpath(layer)),
                "weight": weight
            }})
        layerinfo_dict.update({dir_item: sublayer_info_dict})


def get_purename_and_weight(layer_name):
    """
    It takes a string of the layer name and returns a tuple of the form (layer_name, percentage, number).

    :param layer_name: the name of the layer, such as 'conv1_1#1'
    :return: A tuple of the purename and weight.
    """

    name_weight_list = layer_name.split('#')
    purename = name_weight_list[0]
    if len(name_weight_list) == 1 or int(name_weight_list[1]) <= 0:
        weight = -1  # user doesn't assign a weight of this layer
    else:
        weight = int(name_weight_list[1])
    return purename, weight


def get_file_num(file_path):
    """
    It counts the number of files in a directory
    :return: The number of files in the directory.
    """
    counter = 0
    for root, dirs, files in os.walk(file_path):
        counter = counter + len(files)
    return counter
