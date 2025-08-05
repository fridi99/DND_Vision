from app.Appdata import Appdata as state
import math
from math import cos, sin, tan, sqrt
from math import radians as rad
from Logic.Logic import pythagorean_distance
import numpy as np



class aoe_manager:
    """The aoe_manager class stores and creates all effects that should be saved
       to the battlemap"""
    def __init__(self, cv2_obj):
        self.cv2_obj = cv2_obj
        self.effects = []
    def add_effect(self, effect):
        # effect should be: (kind, position, size) or (kind, start, end)
        self.effects.append(effect)
    def draw(self):
        if state.active:
            col = state.Theme.active
        elif not state.active:
            col = state.Theme.passive
        for eff in self.effects:
            if eff[0] == "s":
                self.cv2_obj.circle(state.overlay, eff[1], eff[2], col, 5)
            if eff[0] == "l":
                self.cv2_obj.line(state.overlay, eff[1], eff[2], col, 10)
            if eff[0] == "c":
                points = generate_cone(eff[1], eff[2])
                self.cv2_obj.polylines(state.overlay, np.int32([points]), True, col, 5)
            if eff[0] == "r":
                points = generate_square(eff[1], eff[2])
                self.cv2_obj.polylines(state.overlay, np.int32([points]), True, col, 5)
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

def generate_line(start, end):
    """
    generates a line constrained into 10 ft steps of distance
    :param start: two number tupel start
    :param end: two number tupel end
    :return: the endpoint as constrained to 10 ft steps
    """
    ang = math.atan2(end[0]-start[0], end[1]-start[1])
    dist = int(round((10 + pythagorean_distance(start[0], start[1], end[0], end[1])), -2)/state.fcal)
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
    dist = int(round((10 + pythagorean_distance(start[0], start[1], end[0], end[1]))/5, -1)/state.fcal)*5
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
    dist = int(round((10 + pythagorean_distance(start[0], start[1], end[0], end[1]))/5, -1) / state.fcal)*5
    point1 = (int(start[0]+math.sin(ang+rad(90))*dist/2), int(start[1]+math.cos(ang+rad(90))*dist/2))
    point2 = (int(start[0] + math.sin(ang - rad(90)) * dist/2), int(start[1] + math.cos(ang - rad(90)) * dist/2))
    point3 = (int(start[0] + math.sin(ang - 0.46) * dist/cos(0.46)), int(start[1] + math.cos(ang - 0.46) * dist/cos(0.46)))
    point4 = (int(start[0] + math.sin(ang + 0.46) * dist / cos(0.46)), int(start[1] + math.cos(ang + 0.46) * dist / cos(0.46)))
    return (point1, point2, point3, point4)