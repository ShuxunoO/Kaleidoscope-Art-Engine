import copy
import hashlib
import random
import sys
from datetime import datetime
from pathlib import Path

sys.path.append(".")
import file_operations as fop
from PIL import Image

from src.CONST_ENV import ENV_PATH as ENV
from src.utils import pre_processing


# TODO：
    # 1. 如果用数量代表权重的图层DNA没有碰撞，一定要记得去反向更新数量权重


def setup_images(layer_configs, layers_info_json):
    # 存放DNA 哈希值的集合
    DNA_set = set()
    # metadata 冲撞的次数
    repetition_num = 0
    for index in range(len(layer_configs)):
        layer_config = layer_configs[index]
        # 这里要重新加载进来
        layers_recipe = layers_info_json[index]
        build_imgs_attributes(layer_config, layers_recipe,
                                DNA_set, repetition_num)

def build_imgs_attributes(layer_config, layers_recipe, DNA_set, repetition_num):
    total_supply = layer_config["totalSupply"]
    token_ID = layer_config["startID"]
    counter = 0
    REPETITION_NUM_LIMIT = 20000
    layers = layer_config["layersOrder"]
    # 构建一个属性列表
    while counter < total_supply and repetition_num < REPETITION_NUM_LIMIT:
        attr_dict = set_metadata(layers_config, layers_recipe)
        attr_list_template = get_attribute_list_template(layers)
        attr_list = get_attribute_list(attr_dict, attr_list_template)
        # 判断是否重复
        attr_DNA = hashlib.sha1(str(attr_list).encode('utf-8')).hexdigest()
        if attr_DNA in DNA_set:
            repetition_num += 1
            print("\n**********Attribute Conflict**********\n")
            continue
        else:
            # 不重复的话更新数值（返回一个图层对象的列表）
            layer_path_list = update_layers_recipe(layers_recipe, attr_dict)
            # 混合图像
            blend_img(layer_path_list, token_ID)
            # 组装metada
            generate_metadata(CONFIG, attr_list, attr_DNA, token_ID)
            # 把dna 添加到 dna_set
            print(f"token_ID: {token_ID} NFT-DNA: {attr_DNA} ")
            DNA_set.add(attr_DNA)
            token_ID += 1
            counter += 1

def set_metadata(layers_config, layers_recipe):
    # 定义属性字典
    attributes_dict = {}

    # 先添加信标层的属性
    for layer in layers_config:
        layer_name = layer["name"]
        layer_info = layers_recipe[layer_name]
        if layer_info["isBeaconLayer"] == True:
            # 将信息填入属性字典
            load_layer_info(layer_name, layer_info, attributes_dict)
            
    # 再添加非信标层的属性
    for layer in layers_config:
        layer_name = layer["name"]
        layer_info = layers_recipe[layer_name]
        if layer_info["isBeaconLayer"] == False:
            beacon_layer = layer_info.get("beaconLayer", None)
            if beacon_layer is not None:
                # 将信息填入属性字典
                beacon = attributes_dict[beacon_layer]["beacon"]
                load_layer_info(layer_name, layer_info, attributes_dict, beacon)
            else:
                # 获取自由层属性
                load_layer_info(layer_name, layer_info, attributes_dict)

    return attributes_dict

def load_layer_info(layer_name, layer_info, attributes_dict, beacon=None):
    # 获取从属子层属性
    beacon, index, target_layer = get_trait_value(layer_info, beacon)
    attributes_dict.update(
    {layer_name : {
        "beacon" : beacon,
        "index" : index,
        "target_layer" : target_layer
    }})


def get_trait_value(layer_info, beacon=None):

    # 信标层
    if layer_info["isBeaconLayer"] == True:
        return get_beaconLayer_value(layer_info)
    
    # 从属子层
    elif layer_info.get("beaconLayer", None):
        return get_subLayer_value(layer_info, beacon)
    
    # 自由层
    else:
        return get_freeLayer_value(layer_info)


def get_beaconLayer_value(layer_info):
    subdir_list = layer_info["sub_dir_info"][0]
    probabilities_list = layer_info["sub_dir_info"][1]
    beacon = random.choices(subdir_list, probabilities_list)[0]
    layer_weight_info_list = layer_info[beacon].get("layer_weight_info_list")
    index, target_layer = random_choose_a_layer(layer_weight_info_list)
    return beacon, index, target_layer

def get_subLayer_value(layer_info, beacon):

    layer_weight_info_list = layer_info[beacon].get("layer_weight_info_list")
    index, target_layer = random_choose_a_layer(layer_weight_info_list)
    return beacon, index, target_layer

def get_freeLayer_value(layer_info):
    layer_weight_info_list = layer_info.get("layer_weight_info_list")
    index, target_layer = random_choose_a_layer(layer_weight_info_list)
    return None, index, target_layer


def random_choose_a_layer(weight_list):

    # 如果用数量代表权重的图层列表为空，则只选择概率权重的图层列表
    if len(weight_list[2]) == 0:
        result = 0
    else:
        # 0 代表用百分比代表权重的图层列表以及各自概率权重
        # 1 代表用数量代表权重的图层列表以及各自数量权重 
        # 3:7的比例可以保证用数量表示权重的图层会被有限选择，防止数量权重的图层到结束还有剩余的情况
        result = random.choices([0, 1], [0.3, 0.7])[0]

    if result == 1:
        layer_list = weight_list[2]
        # 随机选择一个图层的索引
        index = random.choice(list(range(len(layer_list))))
        # 将索引一并返回是为了方便后续更新数量权重
        return index, layer_list[index]

    else:
        layer_list = weight_list[0]
        prob_list = weight_list[1]
        return None, random.choices(layer_list, prob_list)[0]

def get_attribute_list_template(layers):
    attribute_list = []
    for layer in layers:
        attribute_list.append({
            "trait_type": layer["name"],
            "value": ""
        })
    return attribute_list

def get_attribute_list(attr_dict, attr_list_template) -> None:
    for layer_item in attr_list_template:
        layer_name = layer_item["trait_type"]
        layer_info = attr_dict[layer_name]
        layer_item["value"] = layer_info["target_layer"]

def update_layers_recipe(layers, layers_recipe, attr_dict) -> None:
    layer_path_list = []
    for layer in layers:
        layer_name = layer["name"]
        attr_info = attr_dict[layer_name]
        beacon = attr_info["beacon"]
        index = attr_info["index"]
        target_layer = attr_info["target_layer"]
        if index is not None:
            if beacon is not None:
                layer_info = layers_recipe[layer_name][beacon]
                # 更新数量权重
                layer_info["layer_weight_info_list"][3][index] -= 1
                if layer_info["layer_weight_info_list"][3][index] == 0:
                    layer_info["layer_weight_info_list"][2].pop(index)
                    layer_info["layer_weight_info_list"][3].pop(index)
                # 将图层路径加入列表
                layer_path_list.append(layer_info[target_layer])
            else:
                layer_info = layers_recipe[layer_name]
                # 更新数量权重
                layer_info["layer_weight_info_list"][3][index] -= 1
                if layer_info["layer_weight_info_list"][3][index] == 0:
                    layer_info["layer_weight_info_list"][2].pop(index)
                    layer_info["layer_weight_info_list"][3].pop(index)
                # 将图层路径加入列表
                layer_path_list.append(layer_info[target_layer])
    return layer_path_list


# 创建源数据
def generate_metadata(configs, attribute_list, dna, token_ID):
    metadata = {}
    metadata.update({"name": configs["namePrefix"] + " #" + str(token_ID),
    "description": configs["description"],
    "image":configs["baseUri"] + "/" + str(token_ID) + ".png",
    "dna": dna,
    "tokenID": token_ID,
    "date":str(datetime.now()),
    "attributes":attribute_list,
    "poweredBy": "Kaleidoscope-Art-Engine"})
    fop.save_json(ENV.JSON_PATH, f"{str(token_ID)}.json", metadata)


# 合成图像
def blend_img(layer_obj_list, token_ID):
    background = Image.open(layer_obj_list[0]).convert("RGBA")
    for layer in layer_obj_list[1:]:
        img = Image.open(layer).convert("RGBA")
        background.paste(img, (0, 0), img)
    path = ENV.IMAGES_PATH.joinpath(str(token_ID) + '.png')
    background.save(path)


if __name__ == "__main__":
    pre_processing.process()
    CONFIG = fop.load_json(ENV.CONFIG_PATH)
    layers_config = CONFIG["layerConfigurations"][0]["layersOrder"]
    layersInfo_recipe = fop.load_json(ENV.INFO_PATH.joinpath("layersInfo_recipe.json"))
    metadata_dict = set_metadata(layers_config, layersInfo_recipe[0])
    fop.save_json(ENV.INFO_PATH, ENV.INFO_PATH.joinpath("test_metadata_dict.json"), metadata_dict)