# DONE 1: dominant hand detection, only one hand detected
# DONE 3: rectangle
# DONE 4: line length restriction
# DONE 5: cone
# TODO 6: pathing
# TODO 8: moving
# DONE 9: deleting
# DONE 10: hand orientation consideration, keep effects of hand
# BUGFIX 1: hand disapearance makes circle stay improved, testing in progress

from operator import truediv

import cv2
import numpy as np
import mediapipe as mp
import screeninfo
import math
import os
import time
from math import cos, sin, tan, sqrt
from math import radians as rad
import tkinter as tk
from tkinter import filedialog

class aoe_manager:
    """The aoe_manager class stores and creates all effects that should be saved
       to the battlemap"""
    def __init__(self, cv2_obj):
        self.cv2_obj = cv2_obj
        self.effects = []
    def add_effect(self, effect):
        # effect should be: (kind, position, size) or (kind, start, end)
        self.effects.append(effect)
    def draw(self, overlay):
        if active:
            col = Theme.active
        elif not active:
            col = Theme.passive
        for eff in self.effects:
            if eff[0] == "s":
                self.cv2_obj.circle(overlay, eff[1], eff[2], col, 5)
            if eff[0] == "l":
                self.cv2_obj.line(overlay, eff[1], eff[2], col, 10)
            if eff[0] == "c":
                points = generate_cone(eff[1], eff[2])
                self.cv2_obj.polylines(overlay, np.int32([points]), True, col, 5)
            if eff[0] == "r":
                points = generate_square(eff[1], eff[2])
                self.cv2_obj.polylines(overlay, np.int32([points]), True, col, 5)
    def delete_nearest(self, pos):
        least = 9999
        if(len(self.effects) == 0):
            return False
        for eff in self.effects:
            dist = pythagorean_distance(pos[0], pos[1], eff[1][0], eff[1][1])
            if dist < least:
                to_del = eff
                least = dist
        self.effects.remove(to_del)
        return True
    def delete_last(self):
        if (len(self.effects) == 0):
            return False
        self.effects.pop(-1)
        return True

class Theme():
    """This class provides color values and similar to determine apperance of
    effects"""
    passive = (100,0,100)
    active = (60,60,60)
    pointer = (50, 150, 0)
    blowout = (0.15, 110)
    text = (0,0,0)

def pythagorean_distance(x1, y1, x2, y2):
    """
    Simple pythogerian distance between two points
    :param x1: x value of first point
    :param y1: y value of first point
    :param x2: x value of second point
    :param y2: y value of second point
    :return: Distance between points
    """
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)


def grabbing(ind_tip, ind_joint, thum_tip):
    """
    evaluates if the targeted hand is currently pinching. uses distance between
    index tip and upper joint as reference
    :param ind_tip: landmark of tip of index finger
    :param ind_joint: landmark of upper joint of index finger
    :param thum_tip: landmark of tip of thumb
    :return: Boolean
    """
    it_x, it_y = ind_tip.x, ind_tip.y
    ij_x, ij_y = ind_joint.x, ind_joint.y
    tt_x, tt_y = thum_tip.x, thum_tip.y
    # ref = pythagorean_distance(it_x, it_y, ij_x, ij_y)
    ref = 0.03
    if pythagorean_distance(it_x, it_y, tt_x, tt_y)/1.5 < ref:
        return True
    else:
        return False
def generate_line(start, end):
    """
    generates a line constrained into 10 ft steps of distance
    :param start: two number tupel start
    :param end: two number tupel end
    :return: the endpoint as constrained to 10 ft steps
    """
    ang = math.atan2(end[0]-start[0], end[1]-start[1])
    dist = int(round((10 + pythagorean_distance(start[0], start[1], end[0], end[1])), -2)/fcal)
    point = (int(start[0]+math.sin(ang)*dist), int(start[1]+math.cos(ang)*dist))
    return point

def generate_cone(start, end):
    """
    Generates a Cone of fixed size in 10 ft steps. With all edges being of
    equal length the inner angles are 60°
    :param start: two number tupel start
    :param end: two number tupel end
    :return: three point list
    """
    ang = math.atan2(end[0]-start[0], end[1]-start[1])
    dist = int(round((10 + pythagorean_distance(start[0], start[1], end[0], end[1]))/5, -1)/fcal)*5
    point1 = (int(start[0]+math.sin(ang+rad(30))*dist), int(start[1]+math.cos(ang+rad(30))*dist))
    point2 = (int(start[0] + math.sin(ang - rad(30)) * dist), int(start[1] + math.cos(ang - rad(30)) * dist))
    return (start, point1, point2)

def generate_square(start, end):
    """
    Generates a square of equal side length in 10ft steps.
    :param start: two number tupel of center of first side
    :param end: two number tupel of center of opposing side
    :return: four point list
    """
    ang = math.atan2(end[0] - start[0], end[1] - start[1])
    dist = int(round((10 + pythagorean_distance(start[0], start[1], end[0], end[1]))/5, -1) / fcal)*5
    point1 = (int(start[0]+math.sin(ang+rad(90))*dist/2), int(start[1]+math.cos(ang+rad(90))*dist/2))
    point2 = (int(start[0] + math.sin(ang - rad(90)) * dist/2), int(start[1] + math.cos(ang - rad(90)) * dist/2))
    point3 = (int(start[0] + math.sin(ang - 0.46) * dist/cos(0.46)), int(start[1] + math.cos(ang - 0.46) * dist/cos(0.46)))
    point4 = (int(start[0] + math.sin(ang + 0.46) * dist / cos(0.46)), int(start[1] + math.cos(ang + 0.46) * dist / cos(0.46)))
    return (point1, point2, point3, point4)

def ask_for_file():
    """
    WORK IN PROGRESS
    This function asks the user to choose a map to use
    :return: The filepath to chosen map
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(
        title="Select an Image File",
        filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp;*.gif;*.tiff")]
    )
    return file_path

def open_map(i = 0):
    """
    This function opens the map in maps directory at given index
    :param i: index of map to be opened, defaults to zero
    :return: relevant data of the map opened,
    """
    battle_map = cv2.imread("..\maps//" +os.listdir("..\maps")[i])
    if battle_map is None:
        path = ask_for_file()
        battle_map = cv2.imread(path)
        raise FileNotFoundError("Battle map image not found!")
    bmsize_h, bmsize_w = battle_map.shape[0], battle_map.shape[1]
    if bmsize_h > bmsize_w:
        battle_map = cv2.rotate(battle_map, cv2.ROTATE_90_CLOCKWISE)
        bmsize_h, bmsize_w = battle_map.shape[0], battle_map.shape[1]

    ### camera and frame setup ###
    screen = screeninfo.get_monitors()[-1] # fetches info of last monitor attached to device
    scr_w, scr_h = screen.width, screen.height
    aoe_position = (int(scr_w/2), int(scr_h/2))  # Center of image
    scale_w, scale_h = scr_w/bmsize_w, scr_h/bmsize_h
    if(scale_w > scale_h):
        battle_map = cv2.resize(battle_map, (round(bmsize_w*scale_h), round(bmsize_h*scale_h))) # resizes to screen size
    else:
        battle_map = cv2.resize(battle_map, (round(bmsize_w * scale_w), round(bmsize_h * scale_w)))  # resizes to screen size
    return battle_map, aoe_position, scr_w, scr_h

def calibration(cap):
    """
    This function will open and display the calibration code and uses it to
    attempt to produce a scaling factor.
    At the moment this function does not work reliably
    :param cap: The capture instance that the main code uses (camera
    :return: The calculated calibration ratio
    :rtype: float
    """
    calcode = cv2.imread("..\calibration_code.png")
    screen = screeninfo.get_monitors()[-1]  # fetches info of last monitor attached to device
    scr_h, scr_w = screen.height, screen.width
    calcode = cv2.resize(calcode, (scr_h, scr_h))
    calcode = cv2.convertScaleAbs(calcode, alpha=0.6, beta=0)
    cv2.imshow("calibration", calcode)
    cv2.moveWindow("calibration", scr_w, 0)
    qcd = cv2.QRCodeDetector()
    count = 0
    while cap.isOpened():
        ret, cal_frame = cap.read()
        retval, decoded_info, points, straight_qrcode = qcd.detectAndDecodeMulti(cal_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyWindow("calibration")
            ratio = 1
            break

        if retval:
            count += 1
        if count >= 5:
            cv2.destroyWindow("calibration")
            pts = np.int32([points])[0][0]
            ratio = pythagorean_distance(pts[0][0], pts[0][1], pts[2][0], pts[2][1])/208
            break
    return ratio






mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.3, min_tracking_confidence=0.3, max_num_hands=1)

mp_drawing = mp.solutions.drawing_utils

# flags:
dev_mode = False # shows additional information, like hand landmarks

# boolean variable initialization
active = False # flags if the programm is actually manipulating the image
initiert = False # flags if there is anything to show on the map
resizing = False # flags if the code is currently supposed to resize the effect
time_set = False # flags if the start time of timer is set
floating = True # flags if the effect is still being moved
once = False # used to have the code only run once after going inactive


# variable initialization
fcal = 0.87 # factor to scale image to size of table top projection
scalef = 2.2 # the amplification of the finger position when placing the point on the battle map
pointer = (500, 500) # initial position of pointer
map_index = 0 # inital map index in file system
cal_ratio = 1 # initial ratio for calibration. changed by using calibration function
Theme = Theme() # The Theme object is needed as reference for colors


aoe_size = 0
battle_map, aoe_position, scr_w, scr_h = open_map(map_index)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, scr_w)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, scr_h)


### Manager initialization ###
aoe_man = aoe_manager(cv2)
while cap.isOpened():
    
    ret, frame = cap.read()
    frame = frame[int(scr_h*(1/2 - cal_ratio/4)):int(scr_h*(1/2 + cal_ratio/4)), int(scr_w*(1/2 - cal_ratio/4)):int(scr_w*(1/2 + cal_ratio/4))]
    # aritificially zooms into camera feed
    h, w, _ = frame.shape

    #frame = cv2.flip(frame, 1) # only needed when testing to work with built in webcam

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if not ret:
        break
# keymapping:
    # q: quits
    # s: sphere
    # r: square
    # c: cone
    # l: line
    # d: delete closest
    # z: delete latest
    # n: move to next map
    if active:
        key = cv2.waitKey(5) & 0xFF
        once = False
    elif not once:
        key = cv2.waitKey(5) & 0xFF # runs once after being inactivated, to remove whiteout
        once = True
    else:
        key = cv2.waitKey(1000) & 0xFF # stops image from refreshing until a button is pressed to save computing resources
    if key ==  ord("q"):
        # quits program
        break
    if key == ord("s"):
        # creates a sphere
        type = "s"
        floating = True
        active = True
        aoe_start = (0, 0)
    if key == ord("r"):
        # create a square
        type = "r"
        floating = True
        active = True
        aoe_start = (0, 0)
    if key == ord("l"):
        # creates a line
        type = "l"
        floating = True
        active = True
        aoe_start = (0, 0)
    if key == ord("c"):
        # creates a cone
        type = "c"
        floating = True
        active = True
        aoe_start = (0, 0)
    if key == ord("d"):
        # deletes effect closest to pinch
        type = "d"
        floating = True
        active = True
    if key == ord("z"):
        # deletes last effect in manager
        aoe_man.delete_last()
    if key == ord("k"):
        # calibrates battlemap using qr code
        cal_ratio = calibration(cap)
        print(cal_ratio)
    if key == ord("n"):
        # moves to next battlemap
        if (len(os.listdir("..\maps")) != 1):
            if(len(os.listdir("..\maps")) <= map_index+1):
                map_index = 0
            else:
                map_index += 1
            battle_map, aoe_position, scr_w, scr_h = open_map(map_index)

    overlay = battle_map.copy()
    if active:
        overlay = cv2.convertScaleAbs(overlay, alpha=Theme.blowout[0], beta=Theme.blowout[1])
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                initiert = True;
                # Get index finger tip (landmark 8) position
                index_finger = hand_landmarks.landmark[8] # index finger tip
                index_joint = hand_landmarks.landmark[7] # upper joint of index finger
                thumb_tip = hand_landmarks.landmark[4] # thumb tip
                ref_point_lm = [hand_landmarks.landmark[i] for i in [2,5]]
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)


    if initiert and results.multi_hand_landmarks: # should only run if a complete hand is detected, does not always work however
        index_x, index_y = int(index_finger.x * w * 2.5 - 120), int(index_finger.y * h * 2.5 - 150)
        thumb_x, thumb_y = int(thumb_tip.x * w * 2.5 - 120), int(thumb_tip.y * h * 2.5 - 150)
        ref_point = [int((ref_point_lm[0].x + ref_point_lm[1].x)*w*1.25 -120), int((ref_point_lm[0].y + ref_point_lm[1].y)*h*1.25 - 150)]
        print(ref_point)
        pointer = [int(((index_x+thumb_x*2)/3+((index_x+thumb_x*2)/3 - ref_point[0]) + pointer[0]*3)/4),
                   int(((index_y+thumb_y*2)/3+((index_y+thumb_y*2)/3 - ref_point[1]) + pointer[1]*3)/4)]
        if dev_mode:
            mp_drawing.draw_landmarks(overlay, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            cv2.circle(overlay, [index_x, index_y],10, (200,0,0), -1)
            cv2.circle(overlay, ref_point, 10, (50, 255, 0), -1)
            cv2.circle(overlay, [thumb_x, thumb_y], 10, (200, 0, 0), -1)


        if grabbing(index_finger, index_joint, thumb_tip):
            resizing = True
            time_set2 = False
            if not time_set:
                st_time = time.time()
                time_set = True
            del_t = time.time() - st_time
            if del_t > 1:
                floating = False
                time_set = False
                aoe_start = aoe_position
                if(type == "d"):
                    aoe_man.delete_nearest(pointer)
                    type = ""
                    active = False

            elif floating:
                cv2.ellipse(overlay, pointer, (30, 30), 0, 0, del_t * 360, Theme.pointer, -1)
            aoe_size = int(round((10 + pythagorean_distance(int(pointer[0]), int(pointer[1]), aoe_position[0], aoe_position[1])/2)/5, -1)*5/fcal)

        elif(floating):
            aoe_position = pointer
            time_set = False
        elif active:
            resizing = False
            if not time_set2:
                st_time = time.time()
                time_set2 = True
            del_t = time.time() - st_time
            if del_t > 1:
                floating = False
                time_set2 = False
                if type == "s":
                    aoe_man.add_effect((type, aoe_position, aoe_size))
                if type == "l":
                    aoe_man.add_effect((type, aoe_start, end))
                if type == "c":
                    aoe_man.add_effect((type, aoe_start, end))
                if type == "r":
                    aoe_man.add_effect((type, aoe_start, end))
                active = False
            else:
                cv2.ellipse(overlay, pointer, (30, 30), 0, 0, del_t * 360, Theme.pointer, -1)

        if active:
            if type == "s":
                cv2.circle(overlay, aoe_position, aoe_size, Theme.active, 5)
                cv2.putText(overlay, str(round(aoe_size / 50 * fcal, 1) * 5) + "ft", [aoe_position[0]+80,aoe_position[1]+80],
                            cv2.FONT_HERSHEY_SIMPLEX, 1, Theme.text, 2)
            if type == "c" and not floating:
                if resizing:
                    points = generate_cone(aoe_start, pointer)
                    end = pointer
                cv2.polylines(overlay, np.int32([points]), True, Theme.active, 5)
                cv2.putText(overlay, str(round(pythagorean_distance(aoe_start[0], aoe_start[1], end[0], end[1])/9.87/5, -0)*5) + "ft", [aoe_position[0]+80,aoe_position[1]+80],
                            cv2.FONT_HERSHEY_SIMPLEX, 1, Theme.text, 2)
            if type == "r" and not floating:
                if resizing:
                    points = generate_square(aoe_start, pointer)
                    end = pointer
                cv2.polylines(overlay, np.int32([points]), True, Theme.active, 5)
                cv2.putText(overlay, str(round((10 + pythagorean_distance(aoe_start[0], aoe_start[1], end[0], end[1]))/fcal / 11.4/5, -0)*5) + "ft",
                            [aoe_position[0]+80,aoe_position[1]+80],
                            cv2.FONT_HERSHEY_SIMPLEX, 1, Theme.text, 2)
            if type == "l" and aoe_start != (0, 0):
                if resizing:
                    end = generate_line(aoe_start, pointer)
                cv2.line(overlay, aoe_start, end, Theme.active, 10)
                cv2.putText(overlay, str(round(pythagorean_distance(aoe_start[0], aoe_start[1], end[0], end[1])/fcal/13.4, -1)) + "ft", [aoe_position[0]+80,aoe_position[1]+80],
                            cv2.FONT_HERSHEY_SIMPLEX, 1, Theme.text, 2)
            cv2.circle(overlay, pointer, 10, Theme.pointer, -1)


    aoe_man.draw(overlay)
    cv2.imshow("Battlemap", overlay)
    cv2.imshow("Camera", frame)
    cv2.namedWindow("Battlemap", cv2.WINDOW_NORMAL)
    cv2.moveWindow('Battlemap', scr_w, 0)
    cv2.setWindowProperty("Battlemap", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cap.release()
cv2.destroyAllWindows()