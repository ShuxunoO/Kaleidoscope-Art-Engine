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
        attr_dict = set_metadata(layers, layers_recipe)
        if attr_dict is None:
            repetition_num += 1
            print("\n##########--Empty Layer Exception--##########\n")
            continue

        attr_list = get_attribute_list(layers)
        update_attribute_list(attr_dict, attr_list)

        # 判断是否重复
        attr_DNA = hashlib.sha1(str(attr_list).encode('utf-8')).hexdigest()
        if attr_DNA in DNA_set:
            repetition_num += 1
            print("\n**********Attribute Conflict**********\n")
            continue
        else:
            # 不重复的话更新数值（返回一个图层对象的列表）
            layer_path_list = update_layers_recipe(layers, layers_recipe, attr_dict)

            # 混合图像
            blend_img(layer_path_list, token_ID)

            # 组装metada
            generate_metadata(CONFIG, attr_list, attr_DNA, token_ID)

            # 把dna 添加到 dna_set
            print(f"token_ID: {token_ID} NFT-DNA: {attr_DNA} ")
            DNA_set.add(attr_DNA)
            token_ID += 1
            counter += 1
    if counter < total_supply:
        print("**********The number of layers is insufficient, please check the layer settings.**********")
    else:
        print("**********Done!**********")


def set_metadata(layers_order, layers_recipe) -> dict:
    """ randomly select attributes from each layer and return a attribute dictionary
    if choose a empty layer, return None

    Args:
        layers_order (list): a list of layers' name from bottom to top
        e.g. ["background", "body", "head", "eyes", "mouth" ...]
        defined in config.json

        layers_recipe (dict): a dictionary of layers' weight and attributes info

    Returns:
        dict : a dictionary of  the chosed attributes

    """


    # 定义属性字典
    attributes_dict = {}

    # 先添加信标层的属性
    for layer in layers_order:
        layer_name = layer["name"]
        layer_info = layers_recipe[layer_name]
        if layer_info["isBeaconLayer"] == True:
            # 将信息填入属性字典
            target_layer = load_layer_info(layer_name, layer_info, attributes_dict)
            # 如果目标图层为空，则触发空图层异常
            if target_layer is None:
                return None
            
    # 再添加非信标层的属性
    for layer in layers_order:
        layer_name = layer["name"]
        layer_info = layers_recipe[layer_name]
        if layer_info["isBeaconLayer"] == False:
            beacon_layer = layer_info.get("beaconLayer", None)
            if beacon_layer is not None:
                # 将信息填入属性字典
                beacon = attributes_dict[beacon_layer]["beacon"]
                target_layer = load_layer_info(layer_name, layer_info, attributes_dict, beacon)
                if target_layer is None:
                    return None
            else:
                # 获取自由层属性
                target_layer = load_layer_info(layer_name, layer_info, attributes_dict)
                if target_layer is None:
                    return None
                
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
    return target_layer


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

def get_subLayer_value(layer_info, beacon=None):

    layer_weight_info_list = layer_info[beacon].get("layer_weight_info_list")
    index, target_layer = random_choose_a_layer(layer_weight_info_list)
    return beacon, index, target_layer

def get_freeLayer_value(layer_info):
    layer_weight_info_list = layer_info.get("layer_weight_info_list")
    index, target_layer = random_choose_a_layer(layer_weight_info_list)
    return None, index, target_layer


def random_choose_a_layer(weight_list):

    # 0 代表用百分比代表权重的图层列表以及各自概率权重
    # 1 代表用数量代表权重的图层列表以及各自数量权重
    if len(weight_list[0]) == 0:
        # 如果两种图层都没有，那么返回None
        if len(weight_list[2]) == 0:
            # TODO ：抛出异常
            return None, None
        else:
            result = 1
    # 在存在用百分比表示权重的图层的情况下，如果没有用数量表示权重的图层，那么直接返回用百分比表示权重的图层
    elif len(weight_list[2]) == 0:
        result = 0

    # 如果两种图层都有，那么随机选择一种
    else:
        # 2:8的比例可以保证用数量表示权重的图层会被有限选择，防止数量权重的图层到结束还有剩余的情况
        result = random.choices([0, 1], [0.2, 0.8])[0]

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

def get_attribute_list(layers):
    attribute_list = []
    for layer in layers:
        attribute_list.append({
            "trait_type": layer["name"],
            "value": ""
        })
    return attribute_list

def update_attribute_list(attr_dict, attr_list) -> None:
    for layer_item in attr_list:
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
        else:
            if beacon is not None:
                layer_info = layers_recipe[layer_name][beacon]
                layer_path_list.append(layer_info[target_layer])
            else:
                layer_info = layers_recipe[layer_name]
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
    background = background.convert("RGB")
    path = ENV.IMAGES_PATH.joinpath(str(token_ID) + '.png')
    background.save(path)


if __name__ == "__main__":
    pre_processing.process()

    CONFIG = fop.load_json(ENV.CONFIG_PATH)
    layers_config = CONFIG["layerConfigurations"]
    layersInfo_recipe = fop.load_json(ENV.INFO_PATH.joinpath("layersInfo_recipe.json"))
    # metadata_dict = set_metadata(layers_config, layersInfo_recipe[0])
    # fop.save_json(ENV.INFO_PATH, ENV.INFO_PATH.joinpath("test_metadata_dict.json"), metadata_dict)
    setup_images(layers_config, layersInfo_recipe)