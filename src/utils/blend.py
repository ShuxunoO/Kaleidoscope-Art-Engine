import hashlib
import multiprocessing as mp
import random
import sys
import time
from datetime import datetime

sys.path.append(".")
import file_operations as fio
from PIL import Image

from src.CONST_ENV import ENV_PATH as ENV
from src.utils import pre_processing


def setup_images(layer_configs, layers_info_json) -> None:
    """
    An entry function that starts creating NFT media after reading configuration information from here.
    
    Args:
        layer_configs (list): a list of layer's config defined in config.json
        layers_info_json (list): a list of layer's weight info stored in layersInfo_recipe.json
        
    Returns:
        None
    """

    # 存放DNA 哈希值的集合
    DNA_set = set()
    # metadata 冲撞的次数
    repetition_num = 0
    for index in range(len(layer_configs)):
        # 获取图层配置信息, 图层配置信息和图层菜单信息是一一对应的
        layer_config = layer_configs[index]
        layers_recipe = layers_info_json[index]
        # 构建合成NFT用的任务列表
        task_list = generate_collection_metaInfo(layer_config, layers_recipe, DNA_set, repetition_num)
        generate_NFT_collection(task_list)

def generate_collection_metaInfo(layer_config, layers_recipe, DNA_set, repetition_num) -> list:
    """
    Create a metadata list to guide the subsequent synthesis of NFTs,
    where each item in the list contains a combination of NFT components.

    Args:
        layer_config (dict): a layer's config defined in config.json
        layers_recipe (dict): a layer's info defined in layersInfo_recipe.json
        DNA_set (set): a set of DNA hash value, used to check whether the DNA is repeated
        repetition_num (int): the number of repetition,
        if the number of repetition exceeds the limit, the program will stop

    Returns:
        list: a list of tasks for creating NFT media

    """
    task_list = []
    total_supply = layer_config["totalSupply"]
    token_ID = layer_config["startID"]
    counter = 1
    layers = layer_config["layersOrder"]
    REPETITION_NUM_LIMIT = 20000
    # 构建一个属性列表
    while counter < total_supply and repetition_num < REPETITION_NUM_LIMIT:
        # 创建单个NFT的属性字典， 包含随机选择出来的信标层和非信标层属性
        attr_dict = set_metadata(layers, layers_recipe)
        if attr_dict is None:
            repetition_num += 1
            print("\n###############--Empty Layer Exception--###############\n")
            continue
        # 创建一个属性列表模板，用于填充之前随机选择出来的属性
        attr_list = set_attribute_list(layers)
        update_attribute_list(attr_dict, attr_list)

        # 判断是否重复
        attr_DNA = hashlib.sha1(str(attr_list).encode('utf-8')).hexdigest()
        if attr_DNA in DNA_set:
            repetition_num += 1
            print("\n***************Attribute Conflict***************\n")
            continue

        else:
            # 不重复的话更新数值（返回一个图层对象的列表）
            layer_path_list = update_layers_recipe(layers, layers_recipe, attr_dict)

            # 组装metada
            metadata = generate_metadata(CONFIG, attr_list, attr_DNA, token_ID)

            # 把dna 添加到 dna_set
            print(f"token_ID: {token_ID} NFT-DNA: {attr_DNA} ")
            DNA_set.add(attr_DNA)
            token_ID += 1
            counter += 1

            task_list.append((token_ID, metadata, layer_path_list))
    if counter < total_supply:
        print("XXXXXXXXXXXXXXX  The number of layers is insufficient, please check the layer settings.  XXXXXXXXXXXXXXX")
        
    else:
        return task_list
    

def set_metadata(layers_order, layers_recipe) -> dict:
    """ randomly select attributes from each layer and return a attribute dictionary
    if choose a empty layer, return None

    Args:
        layers_order (list): a list of layers' name from bottom to top
        e.g. ["background", "body", "head", "eyes", "mouth" ...] defined in config.json
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

def load_layer_info(layer_name, layer_info, attributes_dict, beacon=None) -> str:
    """load layer info into attributes_dict

    Args:
        layer_name (str): layer's name
        layer_info (dict): layer's info dict
        attributes_dict (dict): attributes dict to store layer info
        beacon (str, optional): a beacon to guide the which subdir to chose. Defaults to None.

    Returns:
        str: the layer be chosen
    """
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
    # 待选择的子目录列表
    subdir_list = layer_info["sub_dir_info"][0]
    # 待选择的子目录概率列表
    probabilities_list = layer_info["sub_dir_info"][1]
    # 按照每个子目录对应的概率选择一个子文件夹作为信标使用
    beacon = random.choices(subdir_list, probabilities_list)[0]
    # 从信标层的子目录中随机选择一个图层
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


def random_choose_a_layer(weight_list) -> tuple:
    """
    Select a layer randomly according to the weight list.

    Args:
        weight_list (list): a list of layer's name and layer's weight info,
        This is a two-dimensional list， 
        where weight_list[0] represents the subfolder list (beacon list)；
        weight_list[1]: probability of each subfolder being selected；
        weight_list[2]: sub-layer list (sub-layer and sub-folder lists will not appear at the same time)；
        and weight_list[3]: probability of selecting the sub-folder list.
        e.g. 
            [
                [subfolder1, subfolder2, subfolder3,],
                [0.1, 0.2, 0.7],
                [],
                []
            ]

            or

            [
                [],
                [],
                [layer1, layer2, layer3, layer4, layer5],
                [0.1, 0.2, 0.3, 0.3, 0.1]
            ]
        defined in layersInfo_recipe.json

    Returns:
        int: the index of the chosen layer
        str: the name of the chosen layer

    """

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

def set_attribute_list(layers) -> list:
    """
    Set the attribute list template according to the layers defined in config.json

    Args:
        layers (list): a list of layers defined in config.json 's keyword "layersOrder"
        
    Returns:
        list: a list of layers containing the layer's trait_type and layer's it's value( default value is "" )),
        e.g.
            [
                {
                    "trait_type": "Earring",
                    "value": ""
                },
                {
                    "trait_type": "Background",
                    "value": ""
                },
                {
                    "trait_type": "Fur",
                    "value": ""
                },
                {
                    "trait_type": "Clothes",
                    "value": ""
                },
                {
                    "trait_type": "Mouth",
                    "value": ""
                },
                {
                    "trait_type": "Eyes",
                    "value": ""
                }
        ]
    """
    attribute_list = []
    for layer in layers:
        attribute_list.append({
            "trait_type": layer["name"],
            "value": ""
        })
    return attribute_list

def update_attribute_list(attr_dict, attr_list) -> None:
    """
    Update the attribute list according to the attr_dict

    Args:
        attr_dict (dict): a dict of layers' attribute info dict which stores the redomly chosen layer's info,
        attr_list (list): a list of layers template to be updated

    Returns:
        None
        
    """
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
    return metadata


def generate_a_NFT(token_info):
    token_ID, metadata, layer_path_list = token_info
    # 混合图像
    blend_a_img(layer_path_list, token_ID)
    # 保存元数据
    fio.save_json(ENV.JSON_PATH, f"{str(token_ID)}.json", metadata)
    print(f"Token #{token_ID} Has Done!")


# 合成图像
def blend_a_img(layer_obj_list, token_ID):
    background = Image.open(layer_obj_list[0]).convert("RGBA")
    for layer in layer_obj_list[1:]:
        img = Image.open(layer).convert("RGBA")
        background.paste(img, (0, 0), img)
    background = background.convert("RGB")
    path = ENV.IMAGES_PATH.joinpath(str(token_ID) + '.png')
    background.save(path)

def generate_NFT_collection(task_list):
    CONFIG = fio.load_json(ENV.CONFIG_PATH)
    num_of_workers = CONFIG["numOfWorkers"]
    # 使用多进程生成NFT
    with mp.Pool(processes=num_of_workers) as p:
        p.map(generate_a_NFT, task_list)

    print("\n---------------  ALL Tokens Done, Congratulations! >(≧∇≦)/ ---------------\n")


if __name__ == "__main__":
    pre_processing.process()
    CONFIG = fio.load_json(ENV.CONFIG_PATH)
    layers_config = CONFIG["layerConfigurations"]
    layersInfo_recipe = fio.load_json(ENV.INFO_PATH.joinpath("layersInfo_recipe.json"))

    start_time = time.time()
    setup_images(layers_config, layersInfo_recipe)
    print(f"Time cost: {time.time() - start_time:.2f}s")
