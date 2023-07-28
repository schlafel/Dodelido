import os

DATA_DIR = os.path.join(os.path.dirname(__file__), r"data")
BACKGROUND_DIR = os.path.join(os.path.dirname(__file__), r"data/backgrounds")


BG_IMG_URL = "https://source.unsplash.com/random"
N_BACKGROUNDS = 200


YAML_PATH = os.path.join(os.path.dirname(__file__), r"dodelido.yaml")


N_TRAIN = 10000
N_VAL = 1e3
N_TEST = 1e3