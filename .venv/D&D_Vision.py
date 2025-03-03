from operator import truediv

import cv2
import numpy as np
import mediapipe as mp
import screeninfo
import math
import os

def pyth_dist(x1, y1, x2, y2):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)

def grabbing(ind_tip, ind_joint, thum_tip):
    it_x, it_y = ind_tip.x, ind_tip.y
    ij_x, ij_y = ind_joint.x, ind_joint.y
    tt_x, tt_y = thum_tip.x, thum_tip.y
    print(pyth_dist(it_x, it_y, tt_x, tt_y))
    print(pyth_dist(it_x, it_y, ij_x, ij_y))
    print("-=-")
    if pyth_dist(it_x, it_y, tt_x, tt_y)/2 < pyth_dist(it_x, it_y, ij_x, ij_y):
        return True
    else:
        return False




screen = screeninfo.get_monitors()[1]
scr_w, scr_h = screen.width, screen.height
zoom_factor = 1.5
scalef = 2.2

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

aoe_position = (400, 300)  # Center of image
aoe_size = 140  # Default size

mp_drawing = mp.solutions.drawing_utils

active = True
initiert = False
resizing = True





battle_map = cv2.imread(r"C:\Users\fried\PycharmProjects\PythonProject\.venv\Scripts\maps//" +os.listdir(r"C:\Users\fried\PycharmProjects\PythonProject\.venv\Scripts\maps")[0])
if battle_map is None:
    raise FileNotFoundError("Battle map image not found!")


battle_map = cv2.resize(battle_map, (scr_w, scr_h))

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, scr_w/2)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, scr_h/2)


while cap.isOpened():
    
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if not ret:
        break
    key = cv2.waitKey(1) & 0xFF

    if key ==  ord("q"):
        break
    if key == ord("a"):
        active = not active
    if key == ord("s"):
        resizing = not resizing

    overlay = battle_map.copy()
    if active:
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                initiert = True;
                # Get index finger tip (landmark 8) position
                index_finger = hand_landmarks.landmark[8]
                index_joint = hand_landmarks.landmark[7]
                thumb_tip = hand_landmarks.landmark[4]
                mp_drawing.draw_landmarks(overlay, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    if initiert:
        index_x, index_y = int(index_finger.x * w), int(index_finger.y * h)
        if grabbing(index_finger, index_joint, thumb_tip):
            if resizing:
                aoe_size = int(
                    pyth_dist(int(index_x * scalef), int(index_y * scalef), aoe_position[0], aoe_position[1]))
            else:
                aoe_position = (int(index_x*scalef), int(index_y*scalef))
        cv2.circle(overlay, aoe_position, aoe_size, (200, 0, 200), 2)
        cv2.putText(overlay, str(aoe_size), aoe_position, cv2.FONT_HERSHEY_SIMPLEX, 1, (200,0,200), 2)



    cv2.imshow("test", overlay)
cap.release()
cv2.destroyAllWindows()