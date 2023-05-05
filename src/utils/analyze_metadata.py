
import re
import sys
import os
from tqdm import tqdm
sys.path.append(".")
from src.CONST_ENV import ENV_PATH as ENV
from src.utils import file_operations as fio


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

def get_collection_base_info(metadata_demo):
    collection_name = metadata_demo.get("name", None).split("#")[0]
    collection_description = metadata_demo.get("description", None)
    
    return collection_name, collection_description
    

def analyze():
    metadata_list = get_file_list(ENV.JSON_PATH)
    prefix_filename_dictionary = get_prefix_filename_dictionary(ENV.IMAGES_PATH)
    metadata_demo = fio.load_json(ENV.JSON_PATH.joinpath(metadata_list[0]))
    collection_name, collection_description = get_collection_base_info(metadata_demo)
    dashboard = {}

    # NFT的总数量
    total_supply = len(metadata_list)
    
    # 属性的编号
    serial_number = 0

    # 属性编号字典
    trait_number_dict = {}
    # 预制属性字典
    dashboard["name"] = collection_name

    # NFT的总数量
    dashboard["total_supply"] = total_supply

    # NFT的项目描述
    dashboard["description"] = collection_description

    # 属性总数
    dashboard["total_traits_count"] = 0

    dashboard["rarity_dashboard"] = {}

    # 属性-编号字典
    dashboard["trait_number_dict"] = {}

    # 编号-属性字典
    dashboard["number_trait_dict"] = {}

    # 属性信息字典
    dashboard["trait_info"] = {}


    for file in tqdm(metadata_list, desc=f"Analyzing{collection_name}metadata", unit="file", total=total_supply, ncols=150, leave=True):
        file_path = ENV.JSON_PATH.joinpath(file)
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
    for trait_type, trait_value in dashboard["trait_info"].items():
        for layer_name, value in trait_value.items():
            value["rarity"] = round(value["trait_count"] / total_supply, 6)
            # 将稀有度加入到稀有度字典中
            dashboard["rarity_dashboard"].update({layer_name: value["rarity"]})
            value["img_list"].sort(key=lambda l: int(re.findall('\d+', l)[0]))

    # 将图层的稀有度按照升序排列
    dashboard["rarity_dashboard"] = dict(sorted(dashboard["rarity_dashboard"].items(), key=lambda item: item[1]))
    
    # 最后将属性字典保存到文件中
    fio.save_json(ENV.INFO_PATH, "Metadata_dashboard.json" , dashboard)
    print("Done!")


if __name__ == "__main__":
    analyze()
