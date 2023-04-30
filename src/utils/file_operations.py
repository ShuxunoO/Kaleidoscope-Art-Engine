import json
import pickle
from pathlib import Path

def save_json(save_path, filename, data) -> None:
    """
    Saves the data to a file with the given filename in the given path
    
    Args:
    :param save_path: The path to the folder where you want to save the file
    :param filename: The name of the file to save
    :param data: The data to be saved

    """
    file_path = Path.joinpath(save_path, filename)
    with open(file_path, 'w', encoding='UTF-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


# load json file
def load_json(config_path) -> dict:
    """
    It loads a JSON file and returns the contents as a Python dictionary
    
    Args:
    :param config_path: The path to the config file
    :return: A dictionary
    """
    with open(config_path, encoding='UTF-8') as f:
        return json.load(f)

# 将数据对象存储为二进制文件
def serialize_save(obj,path) -> None:
    """serialize_file to bit file

    Args:
        obj (obj): the object to be serialized
        path (str): the path to save the serialized file
    """
    with open(path, 'wb') as f:
        pickle.dump(obj, f)

# 读取序列化文件
def serialize_load(path) -> object:
    """load serialized file

    Args:
        path (str): the path to the serialized file

    Returns:
        obj: the object in the serialized file
    """
    with open(path, 'rb') as f:
        obj = pickle.load(f)
        return obj