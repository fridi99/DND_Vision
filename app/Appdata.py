from dataclasses import dataclass
import numpy as np

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
    api_active: bool = True # if the api should be launched or not
    show_stats: bool = False # adds stats like detection confidence


    # variable initialization
    fcal: float = 0.0795 # factor to scale image to size of table top projection
    pointer = np.array([500, 500]) # initial position of pointer
    cal_ratio: float = 1 # initial ratio for calibration. changed by using calibration function
    Theme: 'Theme' = Theme() # The Theme object is needed as reference for colors