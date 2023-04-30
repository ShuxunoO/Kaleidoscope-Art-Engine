
import os
import re
import utils.file_io as fio
from CONST_ENV import CONST_ENV as ENV
from tqdm import tqdm
# TODO:
# 1. 从文件中读取数据
# 2. 遍历文件夹中的metada json文件，查看attributes中的"trait_type"
# 3. 给属性编码，生成一个字典
# 4. 统计每个trait 出现的图片编号与数量


def get_iterable_file_list(path):
    """以迭代器的形式返回文件夹中的文件名

    Args:
        path (str): 文件所在路径

    Yields:
        interable obj: 文件名
    """
    file_list = os.listdir(path)
    for file in file_list:
        yield file


def get_file_list(path):
    """
    以列表的形式返回文件夹中的文件名

    Args:
        path (str): 文件所在路径

    Yields:
        list: 文件列表
    """
    file_list = os.listdir(path)
    return file_list

def get_prefix_filename_dictionary(path):
    """以字典的形式返回文件夹中的文件名，键为文件名的前缀，值为文件名+后缀

    Args:
        path (str): 文件所在路径

    Returns:
        dict: 文件名字典
    """
    file_list = os.listdir(path)
    prefix_filename_dict = {}
    for file in file_list:
        prefix_filename_dict.update({file.split(".")[0]: file})
    return prefix_filename_dict


if __name__ == "__main__":

    reference = fio.load_json(os.path.join(
        ENV.INFO_PATH, "NFT_metadata_V2.json"))
    ranking = "1"
    target_collention = reference[ranking]

    # 项目名称
    NFT_name = target_collention["collection_name"]
    metadata_path = os.path.join(ENV.DATASET_PATH, NFT_name, "metadata")
    img_path = os.path.join(ENV.DATASET_PATH, NFT_name, "img")
    metadata_list = get_file_list(metadata_path)
    prefix_filename_dictionary = get_prefix_filename_dictionary(img_path)

    dashboard = {}
    # NFT的总数量
    total_supply = len(metadata_list)
    # NFT的项目描述
    description = target_collention["contract_metadata"]["openSea"]["description"]

    # 属性的编号
    serial_number = 0

    # 属性编号字典
    trait_number_dict = {}
    # 预制属性字典
    dashboard["name"] = NFT_name
    dashboard["total_supply"] = total_supply
    dashboard["description"] = description

    # 属性总数
    dashboard["total_traits_count"] = 0

    # 属性-编号字典
    dashboard["trait_number_dict"] = {}

    # 编号-属性字典
    dashboard["number_trait_dict"] = {}

    # 属性信息字典
    dashboard["trait_info"] = {}


    for file in tqdm(metadata_list, desc=f"Analyzing{NFT_name}metadata", unit="file", total=total_supply, ncols=150, leave=True):
        file_path = os.path.join(metadata_path, file)
        metadata_info = fio.load_json(file_path)
        attributes = metadata_info["attributes"]

        # 拿到文件名的前缀
        file_name = file.split(".")[0]
        for attribute in attributes:
            trait_type = attribute["trait_type"]
            if not trait_type in dashboard["trait_info"].keys():
                dashboard["trait_info"].update({trait_type: {}})
                trait_number_dict.update({trait_type: {}})
            # 获取属性值
            value = attribute["value"]
            # 如果属性值不在属性字典中，则将属性加入到属性集合中
            if not value in  dashboard["trait_info"][trait_type].keys():
                trait_number_dict[trait_type].update({value: serial_number})
                dashboard["number_trait_dict"].update({str(serial_number): f"{trait_type} of {value}"})
                serial_number += 1
                # 更新属性信息字典
                dashboard["trait_info"][trait_type].update(
                    {value: {
                        "trait_count": 1,
                        "rarity": 0,
                        "img_list": [prefix_filename_dictionary[file_name]]
                    }})
            else:
                dashboard["trait_info"][trait_type][value]["trait_count"] += 1
                dashboard["trait_info"][trait_type][value]["img_list"].append(prefix_filename_dictionary[file_name])
    
    # 更新一下属性编号字典
    dashboard["trait_number_dict"].update(trait_number_dict)
    
    # 更新一下属性总数
    dashboard["total_traits_count"] = serial_number
    
    # 最后计算稀有度并将媒体列表排序
    for key, value in dashboard["trait_info"].items():
        for key, value in value.items():
            value["rarity"] = value["trait_count"] / total_supply
            value["img_list"].sort(key=lambda l: int(re.findall('\d+', l)[0]))
    # 最后将属性字典保存到文件中
    fio.save_json(os.path.join(ENV.DATASET_PATH, NFT_name), "Metadata_dashboard", dashboard)
    print("Done!")

    # fio.save_json(os.path.join(ENV.DATASET_PATH, NFT_name), "test", prefix_filename_dictionary)
