from dataclasses import dataclass

class Theme():
    """This class provides color values and similar to determine apperance of
    effects"""
    passive = (100,0,100)
    active = (60,60,60)
    pointer = (50, 150, 0)
    blowout = (0.15, 110)
    pathing = (100, 0, 100)
    text = (200,200,200)

@dataclass
class Appdata():
    # flags:
    dev_mode: bool = False # shows additional information, like hand landmarks

    # boolean variable initialization
    initiert: bool = False # flags if there is anything to show on the map
    floating: bool = True # flags if the effect is still being moved
    once: bool = False # used to have the code only run once after going inactive


    # variable initialization
    fcal: float = 0.0795 # factor to scale image to size of table top projection
    pointer: tuple = (500, 500) # initial position of pointer
    map_index: int = 0 # inital map index in file system
    cal_ratio: float = 1 # initial ratio for calibration. changed by using calibration function
    aoe_start: tuple = (0,0)
    scr_w,scr_h = 0, 0
    battle_map = None
    aoe_position = (0,0)
    overlay = None
    points = None
    st_time = 0
    Theme: 'Theme' = Theme() # The Theme object is needed as reference for colors
    aoe_man = None