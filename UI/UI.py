from app.Appdata import Appdata as state
import cv2
from Effects.effects import *
from Logic.Logic import *


def keymanager(cap):
    # keymapping:
    # q: quits
    # s: sphere
    # r: square
    # c: cone
    # l: line
    # d: delete closest
    # z: delete latest
    # n: move to next map
    if state.active:
        key = cv2.waitKey(5) & 0xFF
        state.once = False
    elif not state.once:
        key = cv2.waitKey(5) & 0xFF  # runs once after being inactivated, to remove whiteout
        state.once = True
    else:
        key = cv2.waitKey(5) & 0xFF  # stops image from refreshing until a button is pressed to save computing resources
    if key == ord("q"):
        # quits program
        exit()
    if key == ord("s"):
        # creates a sphere
        state.type = "s"
        state.floating = True
        state.active = True
        state.aoe_start = (0, 0)
    if key == ord("r"):
        # create a square
        state.type = "r"
        state.floating = True
        state.active = True
        state.aoe_start = (0, 0)
    if key == ord("l"):
        # creates a line
        state.type = "l"
        state.floating = True
        state.active = True
        state.aoe_start = (0, 0)
    if key == ord("c"):
        # creates a cone
        state.type = "c"
        state.floating = True
        state.active = True
        state.aoe_start = (0, 0)
    if key == ord("d"):
        # deletes effect closest to pinch
        state.type = "d"
        state.floating = True
        state.active = True
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