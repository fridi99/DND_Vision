from dataclasses import dataclass
import numpy as np
import yaml
from yaml import safe_load


class Theme():
    """This class provides color values and similar to determine apperance of
    effects"""
    passive = (100,0,100)
    active = (100,100,100)
    pointer = (50, 150, 0)
    blowout = (0.15, 100)
    pathing = (100, 0, 100)
    text = (200,200,200)

@dataclass
class Appdata():

    # flags:
    dev_mode: bool = False # shows additional information, like hand landmarks
    api_active: bool = False # if the api should be launched or not
    show_stats: bool = False # adds stats like detection confidence


    # variable initialization
    fcal: float = 0.0795 # factor to scale image to size of table top projection
    pointer = np.array([500, 500]) # initial position of pointer
    cal_ratio: float = 1 # initial ratio for calibration. changed by using calibration function
    Theme: 'Theme' = Theme() # The Theme object is needed as reference for colors

def load_config(state, path="config.yaml"):
        with open(path, "r") as f:
            config = yaml.safe_load(f)
            state.dev_mode = config["app"]["dev_mode"]
            state.api_active = config["app"]["api_active"]
            state.show_stats = config["app"]["show_stats"]
            state.fcal = config["app"]["fcal"]
            state.cal_ratio = config["app"]["cal_ratio"]
            state.Theme.passive = config["Theme"]["passive"]
            state.Theme.active = config["Theme"]["active"]
            state.Theme.pointer = config["Theme"]["pointer"]
            state.Theme.blowout = config["Theme"]["blowout"]
            state.Theme.pathing = config["Theme"]["pathing"]
            state.Theme.text = config["Theme"]["text"]

def save_config(dict, path="config.yaml"):
    key = next(iter(dict))
    with open(path, "r") as f:
        config = safe_load(f)
        if not key in config:
            raise KeyError("Key not found in config.yaml. save_config may not add new keys!")
        nested_key = next(iter(dict[key]))
        if not nested_key in config[key]:
            raise KeyError("Key not found in config.yaml. save_config may not add new keys!")
        if type(dict[key][nested_key]) != type(config[key][nested_key]):
            print(type(dict[key][nested_key]), type(config[key][nested_key]))
            raise TypeError("Type of dict not equal. save_config may not change type!")
        config[key].update(dict[key])
    with open(path, "w") as f:
        yaml.safe_dump(config, f)
    return 1
