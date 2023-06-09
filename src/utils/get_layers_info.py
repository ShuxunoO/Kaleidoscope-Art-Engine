import re
import sys
import os
from pathlib import Path
sys.path.append(".")
from src.CONST_ENV import ENV_PATH as ENV
from src.utils.logging_factory import LoggerFactory
from src.utils import exceptions as excp

logf = LoggerFactory()
logger = logf.setup_logger("exceptions", ENV.INFO_PATH.joinpath("exceptions.log"))

def get_dirlist_and_filelist(file_path) -> tuple:
    """
    It takes a file path and returns a files list and a subfolders list in the path

    Args:
    :param file_path: the path to the folder containing the files and subfolders

    Returns:
    :return: A file list and a subfolders list.
    """

    # get subfolders in file_path
    dir_list = [dir_.name for dir_ in Path.iterdir(file_path) if Path.is_dir(dir_)]

    # get the remaining files in file_path
    layer_list = [layer.name for layer in Path.iterdir(file_path) if Path.is_file(layer)]

    return layer_list, dir_list


def get_layers_info(base_path, layer_info, total_Supply) -> dict:
    """
    It takes a base path and a layer info and returns a dictionary of the form {layer_name: layer_info}.

    Args:
    :param base_path: the base path of the layers
    :param layer_info: the layer info of the layers

    Returns:
    :return: A dictionary of the form {layer_name: layer_info}.

    """
    # get the file list and subfolder list in the base path
    current_path = Path.joinpath(base_path, layer_info["name"])
    layer_list, dir_list = get_dirlist_and_filelist(current_path)

    try:
        if len(layer_list) == 0 and len(dir_list) == 0:
            raise excp.NULL_File_Error(f"The file list and subfolder list in layer of  {layer_info['name']} are empty.")
    except excp.NULL_File_Error as e:
        logger.warning(f"{type(e).__name__}: {str(e)}")
        sys.exit(1)

    # a dictionary to store the layers infomation in base path
    layerinfo_dict = {}
    layerinfo_dict.update(layer_info)
    layerinfo_dict.update({
        # remove the suffix and weight to get purename
        "layers_number": get_file_num(current_path),
        "layer_list": layer_list,
        "layer_weights_list": [],
        "sub_dir_list": dir_list,
        "subdir_weights_list": [],
        "is_balanced": False
        })

    # 如果当前目录下有文件，则获取当前目录下的文件信息
    if len(layer_list):
        get_layerinfo_in_currentdir(current_path, layer_list, layerinfo_dict, total_Supply)

    # 如果当前目录下有子目录，则获取子目录下的文件信息
    if len(dir_list):
        get_layerinfo_in_subdir(current_path, dir_list, layerinfo_dict, total_Supply)

    return {layer_info["name"]: layerinfo_dict}


def get_layerinfo_in_currentdir(file_path, layer_list, layerinfo_dict, total_Supply) -> dict:
    """
    get the information of the layers in the current directory

    Args:
    :param file_path: the path to the current directory
    :param layer_list: the list of the layers in the current directory
    :param layerinfo_dict: the dictionary to store the layers information

    Returns:
    :return: A dictionary of the form {layer_name: layer_info}.

    """
    for layer in layer_list:
        layer_name, percentage, amount = get_purename_and_weight(layer)
        # convert amount to Proportions
        if percentage == None and amount != None:
            percentage = round(amount / total_Supply, 6)

        # check the percentage
            try:
                if percentage > 1.0:
                    raise excp.PercentageError(f"The percentage of {layer_name} is {percentage} and greater than 1.0.")
            except excp.PercentageError as e:
                logger.warning(f"{type(e).__name__}: {str(e)}")
                sys.exit(1)

        layer_info = {
            "path": str(file_path.joinpath(layer).resolve()),
            "percentage": percentage,
            "amount": amount
        }
        layerinfo_dict.update({layer_name: layer_info})


def get_layerinfo_in_subdir(base_path, dir_list, layerinfo_dict, total_Supply) -> dict:
    """
    get the information of the layers in the subdirectory

    Args:
    :param base_path: the base path of the layers
    :param dir_list: the list of the subdirectories
    :param layerinfo_dict: the dictionary to store the layers information

    Returns:
    :return: A dictionary of the form {dir_name: layer_info}.
    
    """
    for dir_item in dir_list:
        current_path = base_path.joinpath(dir_item)
        # 获取当前文件夹下的文件列表
        sublayer_list = [layer for layer in  Path.iterdir(current_path) if Path.is_file(layer)]
        sublayer_info_dict = {}
        sublayer_info_dict.update({
                                    "subDir_name": dir_item,
                                    "layers_number": len(sublayer_list),
                                    "layer_list": [layer.name for layer in sublayer_list],
                                    "layer_weights_list": []
                                    })
        # 更新每个文件的信息
        for layer in sublayer_list:
            layer_name, percentage, amount = get_purename_and_weight(layer.name)
            # convert amount to Proportions
            if percentage == None and amount != None:
                percentage = round(amount / total_Supply, 6)

                # check the percentage
                try:
                    if percentage > 1.0:
                        raise excp.PercentageError(f"The percentage of {layer_name} is {percentage} and greater than 1.0.")
                except excp.PercentageError as e:
                    logger.warning(f"{type(e).__name__}: {str(e)}")
                    sys.exit(1)

            sublayer_info_dict.update({layer_name: {
                "path": str(layer),
                "percentage": percentage,
                "amount": amount
            }})
        layerinfo_dict.update({dir_item: sublayer_info_dict})


def get_purename_and_weight(layer) -> tuple:
    """
    It takes a string of the layer name and returns a tuple of the form (layer_name, percentage, number).

    Args:
    :param layer_name: the name of the layer, such as 'layername1%20.png'

    Returns:
    :return: A tuple of the purename and percentage/weight.
    """

    # Legal naming format：layername.png
    # or layername%percentage.png 
    # or layername#weight.pn

    layer_name = None
    percentage = None
    amount = None

    if re.match(r".*%\d+\..*$", layer):
        layer_name, percentage, _ =  re.split("[%.]", layer)
    
    elif re.match(r".*#\d+\..*$", layer):
        layer_name, amount, _ = re.split("[#.]", layer)
    
    elif re.match(r".*\..*$",layer ):
        layer_name, _ =  re.split("[.]", layer)

    else:
        print(f"The layer name {layer} is illegal.")
        exit(1)
    
    # 转换一下数据类型
    if percentage:
        percentage = float(percentage) / 100
    if amount:
        amount = int(amount)

    return layer_name, percentage, amount


def get_file_num(file_path) -> int:
    """
    It counts the number of files in the directory of the file_path.

    Args:
    :param file_path: the path to the directory

    Returns:
    :return: The number of files in the directory.
    """
    counter = 0
    for root, dirs, files in os.walk(file_path):
        counter = counter + len(files)
    return counter

