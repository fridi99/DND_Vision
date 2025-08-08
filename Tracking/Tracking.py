from app.Appdata import Appdata as state
import cv2
import mediapipe as mp
from UI.UI import *
from Effects.effects import *




class tracker:
    """
    This class handles hand tracking and also draws the battlemap, because that is such simple code.

    """
    def __init__(self, cap):
        self.cap = cap
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.3,
                                         min_tracking_confidence=0.3, max_num_hands=1)
        self.mp_drawing = mp.solutions.drawing_utils
        self.end = (0,0)

    def grabbing(self, ind_tip, thum_tip):
        """
        evaluates if the targeted hand is currently pinching. uses distance between
        index tip and upper joint as reference
        :param ind_tip: landmark of tip of index finger
        :param thum_tip: landmark of tip of thumb
        :return: Boolean
        """
        it_x, it_y = ind_tip.x, ind_tip.y
        tt_x, tt_y = thum_tip.x, thum_tip.y
        ref = 0.03
        if pythagorean_distance(it_x, it_y, tt_x, tt_y) / 1.5 < ref:
            return True
        else:
            return False

    def track(self, aoe_man):
        ret, self.frame = self.cap.read()
        self.frame = frame = self.frame[int(state.scr_h*(1/2 - state.cal_ratio/4)):int(state.scr_h*(1/2 + state.cal_ratio/4)),
            int(state.scr_w*(1/2 - state.cal_ratio/4)):int(state.scr_w*(1/2 + state.cal_ratio/4))]
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        if aoe_man.active:
            state.overlay = cv2.convertScaleAbs(state.overlay, alpha=state.Theme.blowout[0],
                                                beta=state.Theme.blowout[1])
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    state.initiert = True;
                    # Get index finger tip (landmark 8) position
                    index_finger = hand_landmarks.landmark[8]  # index finger tip
                    thumb_tip = hand_landmarks.landmark[4]  # thumb tip
                    ref_point_lm = [hand_landmarks.landmark[i] for i in [2, 5]]
                    self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

            if state.initiert and results.multi_hand_landmarks:  # should only run if a complete hand is detected, does not always work however
                index_x, index_y = int(index_finger.x * w * 2.5 - 120), int(index_finger.y * h * 2.5 - 150)
                thumb_x, thumb_y = int(thumb_tip.x * w * 2.5 - 120), int(thumb_tip.y * h * 2.5 - 150)
                ref_point = [int((ref_point_lm[0].x + ref_point_lm[1].x) * w * 1.25 - 120),
                             int((ref_point_lm[0].y + ref_point_lm[1].y) * h * 1.25 - 150)]
                state.pointer = [int(((index_x + thumb_x * 2) / 3 + ((index_x + thumb_x * 2) / 3 - ref_point[0]) +
                                      state.pointer[0] * 3) / 4),
                                 int(((index_y + thumb_y * 2) / 3 + ((index_y + thumb_y * 2) / 3 - ref_point[1]) +
                                      state.pointer[1] * 3) / 4)]
                if state.dev_mode:
                    self.mp_drawing.draw_landmarks(state.overlay, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    cv2.circle(state.overlay, [index_x, index_y], 10, (200, 0, 0), -1)
                    cv2.circle(state.overlay, ref_point, 10, (50, 255, 0), -1)
                    cv2.circle(state.overlay, [thumb_x, thumb_y], 10, (200, 0, 0), -1)

                if aoe_man.active:
                    grab = self.grabbing(index_finger, thumb_tip)
                    self.end = state.aoe_man.shape_creator(grab, self.end)
        self.draw(frame)
    def draw(self, frame):
        state.aoe_man.draw()
        cv2.imshow("Battlemap", state.overlay)
        cv2.imshow("Camera", frame)
        cv2.namedWindow("Battlemap", cv2.WINDOW_NORMAL)
        cv2.moveWindow('Battlemap', state.scr_w, 0)
        cv2.setWindowProperty("Battlemap", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)