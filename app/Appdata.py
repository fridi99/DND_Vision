from dataclasses import dataclass

class Theme():
    """This class provides color values and similar to determine apperance of
    effects"""
    passive = (100,0,100)
    active = (60,60,60)
    pointer = (50, 150, 0)
    blowout = (0.15, 110)
    text = (0,0,0)

@dataclass
class Appdata():
    # flags:
    dev_mode: bool = False # shows additional information, like hand landmarks

    # boolean variable initialization
    active: bool = False # flags if the programm is actually manipulating the image
    initiert: bool = False # flags if there is anything to show on the map
    resizing: bool = False # flags if the code is currently supposed to resize the effect
    time_set: bool = False # flags if the start time of timer is set
    floating: bool = True # flags if the effect is still being moved
    once: bool = False # used to have the code only run once after going inactive


    # variable initialization
    fcal: float = 0.87 # factor to scale image to size of table top projection
    type: ord = ""
    pointer: tuple = (500, 500) # initial position of pointer
    map_index: int = 0 # inital map index in file system
    cal_ratio: float = 1 # initial ratio for calibration. changed by using calibration function
    aoe_start: tuple = (0,0)
    scr_w,scr_h = 0, 0
    battle_map = None
    aoe_position = (0,0)
    overlay = None
    points = None

    Theme: 'Theme' = Theme() # The Theme object is needed as reference for colors