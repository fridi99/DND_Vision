from app.Appdata import Appdata as state
import cv2
from Effects.effects import *
from Logic.Logic import *


def keymanager(cap, aoe_man):
    # keymapping:
    # q: quits
    # s: sphere
    # r: square
    # c: cone
    # l: line
    # d: delete closest
    # z: delete latest
    # n: move to next map
    if aoe_man.active:
        key = cv2.waitKey(5) & 0xFF
        aoe_man.once = False
    elif not state.once:
        key = cv2.waitKey(5) & 0xFF  # runs once after being inactivated, to remove whiteout
        state.once = True
    else:
        key = cv2.waitKey(1000) & 0xFF  # stops image from refreshing until a button is pressed to save computing resources
    if key == ord("q"):
        # quits program
        if aoe_man.active:
            aoe_man.floating = False
            aoe_man.active = False
        else:
            exit()
    if key == ord("s"):
        # creates a sphere
        aoe_man.type = "s"
        aoe_man.floating = True
        aoe_man.active = True
        aoe_man.aoe_start = (0, 0)
    if key == ord("r"):
        # create a square
        aoe_man.type = "r"
        aoe_man.floating = True
        aoe_man.active = True
        aoe_man.aoe_start = (0, 0)
    if key == ord("l"):
        # creates a line
        aoe_man.type = "l"
        aoe_man.floating = True
        aoe_man.active = True
        aoe_man.aoe_start = (0, 0)
    if key == ord("c"):
        # creates a cone
        aoe_man.type = "c"
        aoe_man.floating = True
        aoe_man.active = True
        aoe_man.aoe_start = (0, 0)
    if key == ord("d"):
        # deletes effect closest to pinch
        aoe_man.type = "d"
        aoe_man.floating = True
        aoe_man.active = True
    if key == ord("z"):
        # deletes last effect in manager
        state.aoe_man.delete_last()
    if key == ord("k"):
        # calibrates battlemap using qr code
        state.cal_ratio = calibration(cap)
        print(state.cal_ratio)
    if key == ord("n"):
        # moves to next battlemap
        if (len(os.listdir("maps")) != 1):
            if (len(os.listdir("maps")) <= state.map_index + 1):
                state.map_index = 0
            else:
                state.map_index += 1
            open_map(state.map_index)
    if key == ord("p"):
        # start a pathing operation
        aoe_man.type = "p"
        aoe_man.floating = True
        aoe_man.active = True