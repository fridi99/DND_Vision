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

import tkinter as tk
from tkinter import filedialog
from Effects.effects import *
from dataclasses import dataclass
from app.Appdata import Appdata as state
from Logic.Logic import *


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
    print(file_path)
    return file_path

def open_map(i = 0):
    """
    This function opens the map in maps directory at given index
    :param i: index of map to be opened, defaults to zero
    :return: relevant data of the map opened,
    """
    state.battle_map = cv2.imread("./maps//" + os.listdir("maps")[i])
    if state.battle_map is None:
        path = ask_for_file()
        state.battle_map = cv2.imread(path)
        if state.battle_map is None:
            raise FileNotFoundError("Battle map image not found!")
    bmsize_h, bmsize_w = state.battle_map.shape[0], state.battle_map.shape[1]
    if bmsize_h > bmsize_w:
        state.battle_map = cv2.rotate(state.battle_map, cv2.ROTATE_90_CLOCKWISE)
        bmsize_h, bmsize_w = state.battle_map.shape[0], state.battle_map.shape[1]

    ### camera and frame setup ###
    screen = screeninfo.get_monitors()[-1] # fetches info of last monitor attached to device
    state.scr_w, state.scr_h = screen.width, screen.height
    state.aoe_position = (int(state.scr_w/2), int(state.scr_h/2))  # Center of image
    scale_w, scale_h = state.scr_w/bmsize_w, state.scr_h/bmsize_h
    if(scale_w > scale_h):
        state.battle_map = cv2.resize(state.battle_map, (round(bmsize_w*scale_h), round(bmsize_h*scale_h))) # resizes to screen size
    else:
        state.battle_map = cv2.resize(state.battle_map, (round(bmsize_w * scale_w), round(bmsize_h * scale_w)))  # resizes to screen size
    return state.battle_map, state.aoe_position, state.scr_w, state.scr_h

def calibration(cap):
    """
    This function will open and display the calibration code and uses it to
    attempt to produce a scaling factor.
    At the moment this function does not work reliably
    :param cap: The capture instance that the main code uses (camera
    :return: The calculated calibration ratio
    :rtype: float
    """
    calcode = cv2.imread("calibration_code.png")
    screen = screeninfo.get_monitors()[-1]  # fetches info of last monitor attached to device
    state.scr_h, state.scr_w = screen.height, screen.width
    calcode = cv2.resize(calcode, (state.scr_h, state.scr_h))
    calcode = cv2.convertScaleAbs(calcode, alpha=0.6, beta=0)
    cv2.imshow("calibration", calcode)
    cv2.moveWindow("calibration", state.scr_w, 0)
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

def keymanager():
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
        key = cv2.waitKey(
            1000) & 0xFF  # stops image from refreshing until a button is pressed to save computing resources
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
        aoe_man.delete_last()
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
            state.battle_map, state.aoe_position, state.scr_w, state.scr_h = open_map(state.map_index)


mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.3, min_tracking_confidence=0.3, max_num_hands=1)

mp_drawing = mp.solutions.drawing_utils

aoe_size = 0
state.battle_map, state.aoe_position, state.scr_w, state.scr_h = open_map(state.map_index)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, state.scr_w)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, state.scr_h)


### Manager initialization ###
aoe_man = aoe_manager(cv2)
while cap.isOpened():
    
    ret, frame = cap.read()
    frame = frame[int(state.scr_h*(1/2 - state.cal_ratio/4)):int(state.scr_h*(1/2 + state.cal_ratio/4)), int(state.scr_w*(1/2 - state.cal_ratio/4)):int(state.scr_w*(1/2 + state.cal_ratio/4))]
    # aritificially zooms into camera feed
    h, w, _ = frame.shape

    #frame = cv2.flip(frame, 1) # only needed when testing to work with built in webcam

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if not ret:
        break

    keymanager()

    state.overlay = state.battle_map.copy()
    if state.active:
        state.overlay = cv2.convertScaleAbs(state.overlay, alpha=state.Theme.blowout[0], beta=state.Theme.blowout[1])
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                state.initiert = True;
                # Get index finger tip (landmark 8) position
                index_finger = hand_landmarks.landmark[8] # index finger tip
                index_joint = hand_landmarks.landmark[7] # upper joint of index finger
                thumb_tip = hand_landmarks.landmark[4] # thumb tip
                ref_point_lm = [hand_landmarks.landmark[i] for i in [2,5]]
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)


    if state.initiert and results.multi_hand_landmarks: # should only run if a complete hand is detected, does not always work however
        index_x, index_y = int(index_finger.x * w * 2.5 - 120), int(index_finger.y * h * 2.5 - 150)
        thumb_x, thumb_y = int(thumb_tip.x * w * 2.5 - 120), int(thumb_tip.y * h * 2.5 - 150)
        ref_point = [int((ref_point_lm[0].x + ref_point_lm[1].x)*w*1.25 -120), int((ref_point_lm[0].y + ref_point_lm[1].y)*h*1.25 - 150)]
        print(ref_point)
        state.pointer = [int(((index_x+thumb_x*2)/3+((index_x+thumb_x*2)/3 - ref_point[0]) + state.pointer[0]*3)/4),
                   int(((index_y+thumb_y*2)/3+((index_y+thumb_y*2)/3 - ref_point[1]) + state.pointer[1]*3)/4)]
        if state.dev_mode:
            mp_drawing.draw_landmarks(state.overlay, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            cv2.circle(state.overlay, [index_x, index_y],10, (200,0,0), -1)
            cv2.circle(state.overlay, ref_point, 10, (50, 255, 0), -1)
            cv2.circle(state.overlay, [thumb_x, thumb_y], 10, (200, 0, 0), -1)


        if grabbing(index_finger, index_joint, thumb_tip):
            state.resizing = True
            time_set2 = False
            if not state.time_set:
                st_time = time.time()
                state.time_set = True
            del_t = time.time() - st_time
            if del_t > 1:
                state.floating = False
                state.time_set = False
                state.aoe_start = state.aoe_position
                if(state.type == "d"):
                    aoe_man.delete_nearest(state.pointer)
                    state.type = ""
                    state.active = False

            elif state.floating:
                cv2.ellipse(state.overlay, state.pointer, (30, 30), 0, 0, del_t * 360, state.Theme.pointer, -1)
            aoe_size = int(round((10 + pythagorean_distance(int(state.pointer[0]), int(state.pointer[1]), state.aoe_position[0], state.aoe_position[1])/2)/5, -1)*5/state.fcal)

        elif(state.floating):
            state.aoe_position = state.pointer
            state.time_set = False
        elif state.active:
            state.resizing = False
            if not time_set2:
                st_time = time.time()
                time_set2 = True
            del_t = time.time() - st_time
            if del_t > 1:
                state.floating = False
                time_set2 = False
                if state.type == "s":
                    aoe_man.add_effect((state.type, state.aoe_position, aoe_size))
                if state.type == "l":
                    aoe_man.add_effect((state.type, state.aoe_start, end))
                if state.type == "c":
                    aoe_man.add_effect((state.type, state.aoe_start, end))
                if state.type == "r":
                    aoe_man.add_effect((state.type, state.aoe_start, end))
                state.active = False
            else:
                cv2.ellipse(state.overlay, state.pointer, (30, 30), 0, 0, del_t * 360, state.Theme.pointer, -1)

        if state.active:
            if state.type == "s":
                cv2.circle(state.overlay, state.aoe_position, aoe_size, state.Theme.active, 5)
                cv2.putText(state.overlay, str(round(aoe_size / 50 * state.fcal, 1) * 5) + "ft", [state.aoe_position[0]+80,state.aoe_position[1]+80],
                            cv2.FONT_HERSHEY_SIMPLEX, 1, state.Theme.text, 2)
            if state.type == "c" and not state.floating:
                if state.resizing:
                    points = generate_cone(state.aoe_start, state.pointer)
                    end = state.pointer
                cv2.polylines(state.overlay, np.int32([points]), True, state.Theme.active, 5)
                cv2.putText(state.overlay, str(round(pythagorean_distance(state.aoe_start[0], state.aoe_start[1], end[0], end[1])/9.87/5, -0)*5) + "ft", [state.aoe_position[0]+80,state.aoe_position[1]+80],
                            cv2.FONT_HERSHEY_SIMPLEX, 1, state.Theme.text, 2)
            if state.type == "r" and not state.floating:
                if state.resizing:
                    points = generate_square(state.aoe_start, state.pointer)
                    end = state.pointer
                cv2.polylines(state.overlay, np.int32([points]), True, state.Theme.active, 5)
                cv2.putText(state.overlay, str(round((10 + pythagorean_distance(state.aoe_start[0], state.aoe_start[1], end[0], end[1]))/state.fcal / 11.4/5, -0)*5) + "ft",
                            [state.aoe_position[0]+80,state.aoe_position[1]+80],
                            cv2.FONT_HERSHEY_SIMPLEX, 1, state.Theme.text, 2)
            if state.type == "l" and state.aoe_start != (0, 0):
                if state.resizing:
                    end = generate_line(state.aoe_start, state.pointer)
                cv2.line(state.overlay, state.aoe_start, end, state.Theme.active, 10)
                cv2.putText(state.overlay, str(round(pythagorean_distance(state.aoe_start[0], state.aoe_start[1], end[0], end[1])/state.fcal/13.4, -1)) + "ft", [state.aoe_position[0]+80,state.aoe_position[1]+80],
                            cv2.FONT_HERSHEY_SIMPLEX, 1, state.Theme.text, 2)
            cv2.circle(state.overlay, state.pointer, 10, state.Theme.pointer, -1)


    aoe_man.draw()
    cv2.imshow("Battlemap", state.overlay)
    cv2.imshow("Camera", frame)
    cv2.namedWindow("Battlemap", cv2.WINDOW_NORMAL)
    cv2.moveWindow('Battlemap', state.scr_w, 0)
    cv2.setWindowProperty("Battlemap", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cap.release()
cv2.destroyAllWindows()