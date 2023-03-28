import json
import os
import pickle
import sys
from pathlib import Path

def save_json(save_path, filename, data):
    """
    Saves the data to a file with the given filename in the given path
    
    :param save_path: The path to the folder where you want to save the file
    :param filename: The name of the file to save
    :param data: The data to be saved
    """
    file_path = Path.joinpath(save_path, filename + ".json")
    with open(file_path, 'w', encoding='UTF-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


# load json file
def load_json(config_path):
    """
    It loads a JSON file and returns the contents as a Python dictionary
    
    :param config_path: The path to the config file
    :return: A dictionary
    """
    with open(config_path, encoding='UTF-8') as f:
        return json.load(f)

# 将数据对象存储为二进制文件
def serialize_save(obj,path):
    with open(path, 'wb') as f:
        pickle.dump(obj, f)

# 读取序列化文件
def serialize_load(path):
    with open(path, 'rb') as f:
        obj = pickle.load(f)
        return obj


# 正常写文件
def save_file(file_path, file_name, data):
    file_path = Path.joinpath(file_path, file_name + ".json")
    with open(file_path, 'w') as f:
        f.write(data)

