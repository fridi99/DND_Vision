from app.Appdata import Appdata as state
import cv2
import mediapipe as mp
from UI.UI import *
from Effects.effects import *
from Effects.effects import aoe_man




class tracker:
    """
    This class handles hand tracking and also draws the battlemap, because that is such simple code.

    """
    grab = False
    map_index = 0
    initiert: bool = False
    def __init__(self):
        screen = screeninfo.get_monitors()[-1]
        self.scr_w, self.scr_h = screen.width, screen.height
        self.open_map()
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.scr_w)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.scr_h)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.3,
                                         min_tracking_confidence=0.6, max_num_hands=1)
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
        ref = 0.06
        if pythagorean_distance(it_x, it_y, tt_x, tt_y) < ref:
            return True
        else:
            return False

    def open_map(self):
        """
        This function opens the map in maps directory at given index
        :param i: index of map to be opened, defaults to zero
        :return: relevant data of the map opened,
        """

        try:
            self.battle_map = cv2.imread("./maps//" + os.listdir("maps")[self.map_index])
        except FileNotFoundError:
            print("Directory was not found. If testing only the API file, this is normal")
            print("Will return True")
            return True
        if self.battle_map is None:
            path = ask_for_file()
            self.battle_map = cv2.imread(path)
            if self.battle_map is None:
                raise FileNotFoundError("Battle map image not found!")
        bmsize_h, bmsize_w = self.battle_map.shape[0], self.battle_map.shape[1]
        if bmsize_h > bmsize_w:
            self.battle_map = cv2.rotate(self.battle_map, cv2.ROTATE_90_CLOCKWISE)
            bmsize_h, bmsize_w = self.battle_map.shape[0], self.battle_map.shape[1]

        ### camera and frame setup ###
        screen = screeninfo.get_monitors()[-1]
        self.scr_w, self.scr_h = screen.width, screen.height
        state.aoe_position = (int(self.scr_w / 2), int(self.scr_h / 2))
        scale_w, scale_h = self.scr_w / bmsize_w, self.scr_h / bmsize_h
        if (scale_w > scale_h):
            self.battle_map = cv2.resize(self.battle_map, (round(bmsize_w * scale_h), round(bmsize_h * scale_h)))
        else:
            self.battle_map = cv2.resize(self.battle_map, (round(bmsize_w * scale_w), round(bmsize_h * scale_w)))
        bmsize_h, bmsize_w = self.battle_map.shape[0], self.battle_map.shape[1]
        if bmsize_w < self.scr_w:
            dif = (self.scr_w - bmsize_w)
            pad_l, pad_r = dif // 2, dif - dif // 2
        else:
            pad_l, pad_r = 0, 0
        if bmsize_h < self.scr_h:
            dif = (self.scr_h - bmsize_h)
            pad_t, pad_b = dif // 2, dif - dif // 2
        else:
            pad_t, pad_b = 0, 0
        self.battle_map = cv2.copyMakeBorder(self.battle_map, pad_t, pad_b, pad_l, pad_r, cv2.BORDER_CONSTANT,
                                              (0, 0, 0))

        return True

    def track(self):
        ret, frame = self.cap.read()
        cam_h, cam_w, _ = frame.shape
        frame = frame[int(cam_h*(1/2 - state.cal_ratio/4)):int(cam_h*(1/2 + state.cal_ratio/4)),
            int(cam_w*(1/2 - state.cal_ratio/4)):int(cam_w*(1/2 + state.cal_ratio/4))]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        if aoe_man.active:
            aoe_man.overlay = cv2.convertScaleAbs(aoe_man.overlay, alpha=state.Theme.blowout[0],
                                                beta=state.Theme.blowout[1])
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.initiert = True;
                    # Get index finger tip (landmark 8) position
                    index_finger = hand_landmarks.landmark[8]  # index finger tip
                    thumb_tip = hand_landmarks.landmark[4]  # thumb tip
                    ref_point_lm = [hand_landmarks.landmark[i] for i in [2, 5]]
                    self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)


            if self.initiert and results.multi_hand_landmarks:  # should only run if a complete hand is detected, does not always work however
                index = np.array([index_finger.x * cam_w * 1.25/state.cal_ratio - 120, index_finger.y * cam_h * 1.25/state.cal_ratio - 150], dtype=np.int32)
                thumb = np.array([thumb_tip.x * cam_w/state.cal_ratio * 1.25 - 120, thumb_tip.y * cam_h/state.cal_ratio * 1.25 - 150], dtype=np.int32)
                ref_point = np.array([int((ref_point_lm[0].x + ref_point_lm[1].x) * cam_w/(2*state.cal_ratio) * 1.25 - 120),
                             int((ref_point_lm[0].y + ref_point_lm[1].y) * cam_h/(2*state.cal_ratio) * 1.25 - 150)], dtype=np.int32)
                state.pointer = np.array(((2*(index + thumb * 2)/3 - ref_point) + state.pointer * 6) / 7).astype(int)

                if state.dev_mode:
                    self.mp_drawing.draw_landmarks(aoe_man.overlay, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    cv2.circle(aoe_man.overlay, index, 10, (200, 0, 0), -1)
                    cv2.circle(aoe_man.overlay, ref_point, 10, (0, 30, 200), -1)
                    cv2.circle(aoe_man.overlay, thumb, 10, (200, 0, 0), -1)
                if results.multi_handedness and state.show_stats:
                    for handedness in results.multi_handedness:
                        classification = handedness.classification[0]
                        cv2.putText(aoe_man.overlay, f"detection confidence: {str(round(classification.score, 3))}",
                                    (200, 50) ,cv2.FONT_HERSHEY_SIMPLEX, 1, state.Theme.text, 2)

                if aoe_man.active:
                    self.grab = self.grabbing(index_finger, thumb_tip)
                    if aoe_man.type == "m":
                        aoe_man.move(self.grab)
                    else:
                        self.end = aoe_man.shape_creator(self.grab, self.end)



        self.draw(frame)

    def draw(self, frame):
        """
        displays the battlemap with effects and camera view for the user,
        which is basically a bugfixing feature
        :param frame: the camera image
        :return: None
        """
        aoe_man.draw()
        cv2.imshow("Battlemap", aoe_man.overlay)
        cv2.imshow("Camera", frame)
        cv2.namedWindow("Battlemap", cv2.WINDOW_NORMAL)
        cv2.moveWindow('Battlemap', self.scr_w, 0)
        cv2.setWindowProperty("Battlemap", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

tracker = tracker()