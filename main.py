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
from UI.UI import *
from Effects.effects import *
from dataclasses import dataclass
from app.Appdata import Appdata as state
from Logic.Logic import *




end = (0,0)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.3, min_tracking_confidence=0.3, max_num_hands=1)

mp_drawing = mp.solutions.drawing_utils

open_map(state.map_index)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, state.scr_w)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, state.scr_h)

state.aoe_man = aoe_manager()
state.aoe_man.assign_cv2(cv2)

while cap.isOpened():
    if not state.once:
        path = pathing(cv2, (500, 500))
        path.add_point((800, 500))
        path.add_point((1200,700))
    ret, frame = cap.read()
    frame = frame[int(state.scr_h*(1/2 - state.cal_ratio/4)):int(state.scr_h*(1/2 + state.cal_ratio/4)),
            int(state.scr_w*(1/2 - state.cal_ratio/4)):int(state.scr_w*(1/2 + state.cal_ratio/4))]
    # aritificially zooms into camera feed
    h, w, _ = frame.shape

    #frame = cv2.flip(frame, 1) # only needed when testing to work with built in webcam

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if not ret:
        break

    keymanager(cap)

    state.overlay = state.battle_map.copy()
    if state.active:
        state.overlay = cv2.convertScaleAbs(state.overlay, alpha=state.Theme.blowout[0], beta=state.Theme.blowout[1])
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                state.initiert = True;
                # Get index finger tip (landmark 8) position
                index_finger = hand_landmarks.landmark[8] # index finger tip
                thumb_tip = hand_landmarks.landmark[4] # thumb tip
                ref_point_lm = [hand_landmarks.landmark[i] for i in [2,5]]
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)


    if state.initiert and results.multi_hand_landmarks: # should only run if a complete hand is detected, does not always work however
        index_x, index_y = int(index_finger.x * w * 2.5 - 120), int(index_finger.y * h * 2.5 - 150)
        thumb_x, thumb_y = int(thumb_tip.x * w * 2.5 - 120), int(thumb_tip.y * h * 2.5 - 150)
        ref_point = [int((ref_point_lm[0].x + ref_point_lm[1].x)*w*1.25 -120), int((ref_point_lm[0].y + ref_point_lm[1].y)*h*1.25 - 150)]
        state.pointer = [int(((index_x+thumb_x*2)/3+((index_x+thumb_x*2)/3 - ref_point[0]) + state.pointer[0]*3)/4),
                   int(((index_y+thumb_y*2)/3+((index_y+thumb_y*2)/3 - ref_point[1]) + state.pointer[1]*3)/4)]
        if state.dev_mode:
            mp_drawing.draw_landmarks(state.overlay, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            cv2.circle(state.overlay, [index_x, index_y],10, (200,0,0), -1)
            cv2.circle(state.overlay, ref_point, 10, (50, 255, 0), -1)
            cv2.circle(state.overlay, [thumb_x, thumb_y], 10, (200, 0, 0), -1)



        if state.active:
            grab = grabbing(index_finger, thumb_tip)
            end = shape_creator(grab, end)


    state.aoe_man.draw()
    cv2.imshow("Battlemap", state.overlay)
    cv2.imshow("Camera", frame)
    cv2.namedWindow("Battlemap", cv2.WINDOW_NORMAL)
    cv2.moveWindow('Battlemap', state.scr_w, 0)
    cv2.setWindowProperty("Battlemap", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cap.release()
cv2.destroyAllWindows()