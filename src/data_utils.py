import yaml
from config import *



def get_yaml(path=YAML_PATH):
    with open(path, 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)


    return data

def get_label_dicts(config_dict):
    """
    Function that returns the label dict and the inverted_label dict
    :param config_dict:
    :return:
    """
    label_dict = dict(zip(config_dict["names"],range(config_dict["nc"])))
    label_dict_inv = dict([(value, key) for key, value in label_dict.items()])

    return label_dict,label_dict_inv




if __name__ == '__main__':
    data = get_yaml()
    print(data)

