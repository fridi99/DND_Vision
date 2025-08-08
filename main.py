# DONE 1: dominant hand detection, only one hand detected
# DONE 3: rectangle
# DONE 4: line length restriction
# DONE 5: cone
# TODO 6: pathing
# TODO 8: moving
# DONE 9: deleting
# DONE 10: hand orientation consideration, keep effects of hand
# BUGFIX 1: hand disapearance makes circle stay; improved, testing in progress
# BUGFIX 2: properly cleanup pointer and the like after placing effect


from UI.UI import *
from Effects.effects import *

from Logic.Logic import *
from Tracking.Tracking import tracker

open_map(state.map_index)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, state.scr_w)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, state.scr_h)
tracker = tracker(cap)
state.aoe_man = aoe_manager()
state.aoe_man.assign_cv2(cv2)

while cap.isOpened():
    keymanager(cap, state.aoe_man)
    state.overlay = state.battle_map.copy()
    tracker.track(state.aoe_man)

cap.release()
cv2.destroyAllWindows()