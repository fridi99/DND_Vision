from app.Appdata import Appdata as state
import cv2
from Effects.effects import *
from Logic.Logic import *
from Effects.effects import aoe_man

class keymanager:
    once = False
    def __init__(self, tracker):
        self.cap = tracker.cap
        self.track = tracker
    def process_keypress(self):
        # keymapping:
        # q: quits
        # s: sphere
        # r: square
        # c: cone
        # l: line
        # p: pathing
        # d: delete closest
        # z: delete latest
        # n: move to next map
        if aoe_man.active:
            key = cv2.waitKey(5) & 0xFF
            aoe_man.once = False
        elif not aoe_man.once:
            key = cv2.waitKey(5) & 0xFF  # runs once after being inactivated, to remove whiteout
            aoe_man.once = True
        else:
            key = cv2.waitKey(0) & 0xFF  # stops image from refreshing until a button is pressed to save computing resources
        if key == ord("q"):
            # quits program
            if aoe_man.active:
                aoe_man.floating = False
                aoe_man.active = False
            else:
                exit()
        if key == ord("s"):
            # creates a sphere
            aoe_man.activate_type("s")
        if key == ord("r"):
            # create a square
            aoe_man.activate_type("r")
        if key == ord("l"):
            # creates a line
            aoe_man.activate_type("l")
        if key == ord("c"):
            # creates a cone
            aoe_man.activate_type("c")
        if key == ord("p"):
            # start a pathing operation
            aoe_man.activate_type("p")
        if key == ord("d"):
            # deletes effect closest to pinch
            aoe_man.type = "d"
            aoe_man.floating = True
            aoe_man.active = True
        if key == ord("z"):
            # deletes last effect in manager
            aoe_man.delete_last()
        if key == ord("k"):
            # calibrates battlemap using qr code
            state.cal_ratio = calibration(self.cap)
            print(state.cal_ratio)
        if key == ord("n"):
            # moves to next battlemap
            if (len(os.listdir("maps")) != 1):
                if (len(os.listdir("maps")) <= self.track.map_index + 1):
                    self.track.map_index = 0
                else:
                    self.track.map_index += 1
                self.track.open_map()
        if key == ord("m"):
            aoe_man.active = True
            aoe_man.type = "m"
