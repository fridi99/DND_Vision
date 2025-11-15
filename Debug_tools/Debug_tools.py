import numpy as np


from Effects.effects import aoe_man


class debug_point:
    def __init__(self, point, cv2):
        self.x, self.y = point
        self.cv2 = cv2
    def draw(self):
        aoe_man.overlay = self.cv2.putText(aoe_man.overlay, f"{self.x}  {self.y}",
        (self.x, self.y), self.cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))
        aoe_man.overlay = self.cv2.circle(aoe_man.overlay, (self.x+50, self.y+50), 5, (255, 255, 255), -1)