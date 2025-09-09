# DONE 1: dominant hand detection, only one hand detected
# DONE 3: rectangle
# DONE 4: line length restriction
# DONE 5: cone
# DONE 6: forced pathing to snap to 5 feet steps
# DONE 8: moving
# DONE 9: deleting
# TODO 10: make choosing a size easier and more reliable
# DONE 10: hand orientation consideration, keep effects of hand
# BUGFIX 1: hand disappearance makes circle stay; improved, testing in progress
# BUGFIX 2: properly cleanup pointer and the like after placing effect


from UI.UI import *
from Effects.effects import *

from Logic.Logic import *
from Tracking.Tracking import tracker
from API.api import app
import API.api as api
from Effects.effects import aoe_man


aoe_man.assign_cv2(cv2)
keyman = keymanager(tracker)
if state.api_active:
    api.start_server()

while tracker.cap.isOpened():
    keyman.process_keypress()
    aoe_man.overlay = tracker.battle_map.copy()
    tracker.track()

tracker.cap.release()
cv2.destroyAllWindows()
