import re
import sys

sys.path.append(".")
import file_operations as fop

from src.CONST_ENV import ENV_PATH as ENV

def normalize_probility_list(prob_list):
    """normalize the probility list.

    Args: 
        prob_list (list): the probility list to be normalized.

    Returns:
        list: the normalized probility list.
    """
    prob_sum = sum(prob_list)
    if prob_sum == 0:
        return prob_list
    
    prob_list_updated = []
    pro_sum = 1.0
    for i in range(len(prob_list) - 1):
        new_prob = round(prob_list[i] / prob_sum, 6)
        prob_list_updated.append(new_prob)
        pro_sum -= new_prob
    prob_list_updated.append(round(pro_sum, 6))
    return prob_list_updated


def make_layer_list_recipe(layer_info) -> dict:
    """ make the layer list recipe.

    Args:
        layer_info (dict): the layer info of the layer_info.

    Returns:
        dict: a dict contains layer paths with a normalized layer probability list.

    """
    layer_list = layer_info.get("layer_list")
    layer_list_recipe = {}

    if "isBeaconLayer" in layer_info.keys():
        layer_list_recipe["isBeaconLayer"] = layer_info.get("isBeaconLayer")

    if "beaconLayer" in layer_info.keys():
        layer_list_recipe["beaconLayer"] = layer_info.get("beaconLayer")

    layer_list_recipe["layer_weight_info_list"] = []
    # List of layers with percentage in their names
    layer_with_percentage = []
    layer_percentage_list = []

    # List of layers with number in their names
    layer_with_num = []
    layer_num_list = []

    for layer in layer_list:
        layer_name = re.split("[%#.]", layer)[0]
        layer_info_item = layer_info.get(layer_name)
        layer_list_recipe.update({layer_name: layer_info_item.get("path")})

        if layer_info_item.get("amount") == None:
            layer_with_percentage.append(layer_name)
            layer_percentage_list.append(layer_info_item.get("percentage"))
        else:
            layer_with_num.append(layer_name)
            layer_num_list.append(layer_info_item.get("amount"))

    layer_list_recipe["layer_weight_info_list"].append(layer_with_percentage)

    # normalize the probility list
    normalized_prob_list = normalize_probility_list(layer_percentage_list)
    layer_list_recipe["layer_weight_info_list"].append(normalized_prob_list)
    layer_list_recipe["layer_weight_info_list"].append(layer_with_num)
    layer_list_recipe["layer_weight_info_list"].append(layer_num_list)
    return layer_list_recipe


def make_subdir_list_recipe(layer_info):
    """ make the subdir list recipe.

    Args:
        layer_info (dict): the layer info of the layer_info.

    Returns:
        dict: a dict contains layer paths with a normalized layer probability list.
        
    """
    sub_dir_list = layer_info.get("sub_dir_list")
    sub_dir_list_recipe = {}
    
    if "isBeaconLayer" in layer_info.keys():
        sub_dir_list_recipe["isBeaconLayer"] = layer_info.get("isBeaconLayer")
        
    if "beaconLayer" in layer_info.keys():
        sub_dir_list_recipe["beaconLayer"] = layer_info.get("beaconLayer")

    sub_dir_list_recipe.update({"sub_dir_info": [layer_info.get("sub_dir_list"), layer_info.get("subdir_weights_list")]})
    for sub_dir in sub_dir_list:
        sub_dir_info = layer_info.get(sub_dir)
        layer_list_recipe = make_layer_list_recipe(sub_dir_info)
        sub_dir_list_recipe[sub_dir] = layer_list_recipe
    return sub_dir_list_recipe


def generate_NFT_recipe(layer_info_dict) -> dict:
    """load the layer info from the layer_info_path.

    Args:
        layer_info_dict (dict): the layer info of the layer_info.

    Returns:
        dict: a dict contains layer paths with a normalized layer probability list.
    
    """
    layers_recipe = []
    for info_item in layer_info_dict:
        layers_recipe_item = {}
        layers_info = info_item.get("layers_info")
        for layer_name, layer_info in layers_info.items():
            if len(layer_info.get("layer_list")) != 0:
                layer_list_recipe = make_layer_list_recipe(layer_info)
                layers_recipe_item[layer_name] = layer_list_recipe
            if len(layer_info.get("sub_dir_list")) != 0:
                subdie_list_recipe = make_subdir_list_recipe(layer_info)
                layers_recipe_item[layer_name] = subdie_list_recipe
        layers_recipe.append(layers_recipe_item)
    return layers_recipe


if __name__ == "__main__":
    layers_info = fop.load_json(ENV.INFO_PATH.joinpath("layersInfo_update.json"))
    layers_recipe = generate_NFT_recipe(layers_info)
    fop.save_json(ENV.INFO_PATH,"layersInfo_recipe.json", layers_recipe)