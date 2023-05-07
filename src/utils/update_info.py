import os
import random
import sys
import re
from pathlib import Path

from tqdm import tqdm

import utils.file_operations as fio

sys.path.append('..')
from CONST_ENV import ENV_PATH as PATH


# 更新json信息
def update_metadata(CONFIG):
    json_path = PATH.JSON_PATH
    file_list =  os.listdir(json_path)
    for file_item in tqdm(file_list, desc='Updating Metadata ',unit= "piece", postfix={'value': len(file_list)}):
        # 加载文件
        json_file = fio.load_json(json_path.joinpath(file_item))
        # 修改信息
        token_ID = str(json_file["tokenID"])
        json_file["name"] = CONFIG["namePrefix"] + " #" + token_ID
        json_file["description"] = CONFIG["description"]
        json_file["image"] = CONFIG["baseUri"] + "/" + token_ID + ".png"
        # 存储文件
        fio.save_json(json_path, token_ID, json_file)
    print("Done")

def count_layer_distribution():
    pass

# 打乱某一区间内的图像和json
def shuffle(start, end):
    # 排出一些不用修改的情况
    if end - start <= 0:
        return
    json_path = PATH.JSON_PATH
    img_path = PATH.IMAGES_PATH
    file_list = list(range(start, end+1))
    file_list_shuffled = list(range(start, end+1))
    random.shuffle(file_list_shuffled)
    length = end - start + 1
    print("original file list",file_list)
    print("shuffle file list",file_list_shuffled)
    # 给图片起一个临时名字
    temp_img_name_list = batch_assignment_temporary_name(start, end, img_path, suffix =".png")
    # 给json文件起一个临时名字
    temp_json_name_list = batch_assignment_temporary_name(start, end, json_path, suffix =".json")
    # 修改json文件中的内容
    print("temp_img_name_list",temp_img_name_list)
    print("temp_json_name_list",temp_json_name_list)
    modify_json_file(temp_json_name_list, file_list_shuffled, json_path)

    for index in tqdm(range(length), desc='Shuffling',unit= "piece", postfix={'value': length}):
        new_ID = file_list_shuffled[index]
        new_img_name = str(new_ID) + ".png"
        new_json_name = str(new_ID) + ".json"
        # 更改图片文件名字
        os.rename(img_path.joinpath(temp_img_name_list[index]),img_path.joinpath(new_img_name))
        # 更改json文件名字
        os.rename(json_path.joinpath(temp_json_name_list[index]),json_path.joinpath(new_json_name))

# 给要洗牌的图片和json文件起一个临时的名字，格式为：原始名称 + _.suffix
def batch_assignment_temporary_name(start, end, file_path, suffix):
    # 排出一些不用修改的情况
    if end - start <= 0:
        return
    temp_name = []
    file_list = list(range(start, end+1))
    length = end - start + 1
    for item in tqdm(file_list, desc='Assignment temporary name',unit= "piece", postfix={'value': length}):
        original_img_name = str(item) + suffix
        new_img_name = str(item) + "_" + suffix
        temp_name.append(new_img_name)
        os.rename(file_path.joinpath(original_img_name),file_path.joinpath(new_img_name))
    return temp_name

# 修改json文件内的内容
def modify_json_file(temp_json_name_list, file_list_shuffled, file_path):
    length = len(temp_json_name_list)
    for index in tqdm(range(length), desc='Modify json file',unit= "piece", postfix={'value': length}):
        file_name = temp_json_name_list[index]
        new_ID = file_list_shuffled[index]
        # 取出json文件
        json_file = fio.load_json(file_path.joinpath(file_name))
        # 用正则表达式修改json数据
        json_file["name"] = re.sub(r"""\#[0-9]*""", "#" + str(new_ID), json_file["name"])
        json_file["image"] = re.sub(r"""/[0-9]*.png""", "/" + str(new_ID) + ".png", json_file["image"])
        json_file["tokenID"] = new_ID
        # 存储
        fio.save_json(file_path, file_name.split(".")[0], json_file)


