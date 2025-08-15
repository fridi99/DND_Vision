from app.Appdata import Appdata as state
import math
from math import cos, sin, tan, sqrt
from math import radians as rad
from Logic.Logic import pythagorean_distance
import numpy as np
import cv2
import time



class aoe_manager:
    """The aoe_manager class stores and creates all effects that should be saved
       to the battlemap"""
    active = False
    path = None
    st_time = 0
    time_set = False
    time_set2 = False
    resizing = False
    size = 0
    points = None
    aoe_start = (0,0)
    floating = False

    def __init__(self):
        self.effects = []
        self.type = ""

    def assign_cv2(self, cv2_obj):
        """to prevent circular import the cv2 object is set using this function"""
        self.cv2_obj = cv2_obj

    def add_effect(self, effect):
        # effect should be: (kind, position, size) or (kind, start, end)
        # The effect may also be the type and a class object, like the pathing object
        self.effects.append(effect)

    def draw(self):
        if self.active:
            color = state.Theme.active
        elif not self.active:
            color = state.Theme.passive
        for eff in self.effects:
            if eff[0] == "s":
                self.cv2_obj.circle(state.overlay, eff[1], eff[2], color, 5)
            if eff[0] == "l":
                self.cv2_obj.line(state.overlay, eff[1], eff[2], color, 10)
            if eff[0] == "c":
                points = self.generate_cone(eff[1], eff[2])
                self.cv2_obj.polylines(state.overlay, np.int32([points]), True, color, 5)
            if eff[0] == "r":
                points = self.generate_square(eff[1], eff[2])
                self.cv2_obj.polylines(state.overlay, np.int32([points]), True, color, 5)
            if eff[0] == "p":
                eff[1].draw(self.active)

    def delete_nearest(self, pos):
        """
        This function finds the closest effect to the pointer and deletes it
        :param pos: tuple, koordinates of the pointer
        :return: bool, if an effect was deleted or not
        """
        least = 999_999
        if len(self.effects) == 0:
            return False
        for eff in self.effects:
            dist = pythagorean_distance(pos[0], pos[1], eff[1][0], eff[1][1])
            if dist < least:
                to_del = eff
                least = dist
        self.effects.remove(to_del)
        return True
    def delete_last(self):
        if len(self.effects) == 0:
            return False
        self.effects.pop(-1)
        return True

    def generate_line(self, start, end):
        """
        generates a line constrained into 10 ft steps of distance
        :param start: two number tupel start
        :param end: two number tupel end
        :return: the endpoint as constrained to 10 ft steps
        """
        ang = math.atan2(end[0] - start[0], end[1] - start[1])
        dist = int(round((10 + pythagorean_distance(start[0], start[1], end[0], end[1])) * state.fcal, -1))
        dist = dist / state.fcal
        point = (int(start[0] + math.sin(ang) * dist), int(start[1] + math.cos(ang) * dist))
        return point

    def generate_cone(self, start, end):
        """
        Generates a Cone of fixed size in 5 ft steps. With all edges being of
        equal length the inner angles are 60°
        :param start: two number tuple start
        :param end: two number tuple end
        :return: three point list
        """
        ang = math.atan2(end[0] - start[0], end[1] - start[1])
        dist = int(round((10 + pythagorean_distance(start[0], start[1], end[0], end[1])) * state.fcal/5, -0)) * 5
        dist = dist/state.fcal
        point1 = (int(start[0] + math.sin(ang + rad(30)) * dist), int(start[1] + math.cos(ang + rad(30)) * dist))
        point2 = (int(start[0] + math.sin(ang - rad(30)) * dist), int(start[1] + math.cos(ang - rad(30)) * dist))
        return start, point1, point2

    def generate_square(self, start, end):
        """
        Generates a square of equal side length in 10ft steps.
        :param start: two number tupel of center of first side
        :param end: two number tupel of center of opposing side
        :return: four point list
        """
        ang = math.atan2(end[0] - start[0], end[1] - start[1])
        dist = int(round((10+pythagorean_distance(start[0], start[1], end[0], end[1]))* state.fcal/ 5, -0)) * 5
        dist = dist/state.fcal
        point1 = (int(start[0] + math.sin(ang + rad(90)) * dist / 2),
                  int(start[1] + math.cos(ang + rad(90)) * dist / 2))
        point2 = (int(start[0] + math.sin(ang - rad(90)) * dist / 2),
                  int(start[1] + math.cos(ang - rad(90)) * dist / 2))
        point3 = (int(start[0] + math.sin(ang - 0.46) * dist / cos(0.46)),
                  int(start[1] + math.cos(ang - 0.46) * dist / cos(0.46)))
        point4 = (int(start[0] + math.sin(ang + 0.46) * dist / cos(0.46)),
                  int(start[1] + math.cos(ang + 0.46) * dist / cos(0.46)))
        return point1, point2, point3, point4

    def shape_creator(self, grab, end):
        """
        This function generates shapes on the battlemap
        :param grab: wether a grabing gesture is detected
        :param end: the end point of the effect
        :return: the newly chosen end point of the effect
        """
        if grab:
            self.resizing = True
            self.time_set2 = False
            if not self.time_set:
                self.st_time = time.time()
                self.time_set = True
            del_t = time.time() - self.st_time
            if del_t > 0.4:
                self.floating = False
                self.time_set = False
                self.aoe_start = state.aoe_position
                if self.type == "d":
                    state.aoe_man.delete_nearest(state.pointer)
                    self.type = ""
                    self.active = False

            elif self.floating:
                cv2.ellipse(state.overlay, state.pointer, (30, 30), 0, 0, del_t / 0.4 * 360, state.Theme.pointer, -1)
            state.aoe_size = int(round((10 + pythagorean_distance(int(state.pointer[0]), int(state.pointer[1]), 
                                                                  state.aoe_position[0], state.aoe_position[1]) / 2) / 5
                                       ,-1) * 5 * state.fcal)

        elif self.floating:
            state.aoe_position = state.pointer
            self.time_set = False
        elif self.active:
            self.resizing = False
            if not self.time_set2:
                self.st_time = time.time()
                self.time_set2 = True
            del_t = time.time() - self.st_time
            if del_t > 0.4:
                self.floating = False
                self.time_set2 = False
                if self.type == "s":
                    state.aoe_man.add_effect((self.type, state.aoe_position, int(self.size/state.fcal)))
                if self.type == "l":
                    state.aoe_man.add_effect((self.type, self.aoe_start, end))
                if self.type == "c":
                    state.aoe_man.add_effect((self.type, self.aoe_start, end))
                if self.type == "r":
                    state.aoe_man.add_effect((self.type, self.aoe_start, end))
                if self.type == "p":
                    state.aoe_man.add_effect((self.type, self.path))
                    self.path = None
                self.active = False
                self.once = False
            else:
                cv2.ellipse(state.overlay, state.pointer, (30, 30), 0, 0, del_t / 0.4 * 360, state.Theme.pointer, -1)

        if self.type == "s":
            self.size = int(round(pythagorean_distance(state.aoe_position[0], state.aoe_position[1],
                                           state.pointer[0], state.pointer[1]) * state.fcal / 5, -0) * 5)
            cv2.circle(state.overlay, state.aoe_position, int(self.size/state.fcal), state.Theme.active, 5)
            cv2.putText(state.overlay, str(self.size) + "ft",
                        [state.aoe_position[0] + 80, state.aoe_position[1] + 80],
                        cv2.FONT_HERSHEY_SIMPLEX, 1, state.Theme.text, 2)
        if self.type == "c" and not self.floating:
            if self.resizing:
                self.points = self.generate_cone(self.aoe_start, state.pointer)
                end = state.pointer
            cv2.polylines(state.overlay, np.int32([self.points]), True, state.Theme.active, 5)
            size = round((10 + pythagorean_distance(
                self.aoe_start[0], self.aoe_start[1], end[0], end[1])) * state.fcal / 5,-0) * 5

            cv2.putText(state.overlay, str(size) + "ft", 
                        [state.aoe_position[0] + 80, state.aoe_position[1] + 80], 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, state.Theme.text, 2)
        if self.type == "r" and not self.floating:
            if self.resizing:
                self.points = self.generate_square(self.aoe_start, state.pointer)
                end = state.pointer
            size = round(
                (10 + pythagorean_distance(self.aoe_start[0], self.aoe_start[1], end[0], end[1])) * state.fcal / 5,
                -0) * 5
            cv2.polylines(state.overlay, np.int32([self.points]), True, state.Theme.active, 5)
            cv2.putText(state.overlay, str(size) + "ft",
                        [state.aoe_position[0] + 80, state.aoe_position[1] + 80],
                        cv2.FONT_HERSHEY_SIMPLEX, 1, state.Theme.text, 2)
        if self.type == "l" and self.aoe_start != (0, 0):
            if self.resizing:
                end = self.generate_line(self.aoe_start, state.pointer)
            cv2.line(state.overlay, self.aoe_start, end, state.Theme.active, 10)
            size = round(
                (10 + pythagorean_distance(self.aoe_start[0], self.aoe_start[1], end[0], end[1])) * state.fcal,
                -1)
            cv2.putText(state.overlay, str(size) + "ft", [state.aoe_position[0] + 80, state.aoe_position[1] + 80],
                        cv2.FONT_HERSHEY_SIMPLEX, 1, state.Theme.text, 2)
        cv2.circle(state.overlay, state.pointer, 10, state.Theme.pointer, -1)
        if self.type == "p":
            if self.resizing:
                if self.path is None:
                    self.path = pathing(cv2, state.pointer)
                else:
                    self.path.add_point(state.pointer)
            if not self.path is None:
                self.path.draw(self.active)
        return end


class pathing:
    """This class is used to define a pathing object, that allows the user to
    measure the distance of an arbitrary path"""
    def __init__(self, cv2_obj, start):
        self.cv2_obj = cv2_obj
        self.path = [start]
        self.dist = 0

    def add_point(self, point):
        # I would prefer this function to strictly allow only 5 ft steps, but
        # did not make it work yet
        if pythagorean_distance(self.path[-1][0], self.path[-1][1],
                                point[0], point[1])*state.fcal > 5:
            self.path.append(point)
            self.dist += round(pythagorean_distance(self.path[-2][0], self.path[-2][1],
                                          self.path[-1][0], self.path[-1][1])*state.fcal)

    def draw(self, active):
        if active:
            color = state.Theme.active
        elif not active:
            color = state.Theme.passive
        self.cv2_obj.polylines(state.overlay, np.int32([self.path]), False, color, 5)
        self.cv2_obj.putText(state.overlay, str(self.dist) + "ft", self.path[-1], cv2.FONT_HERSHEY_SIMPLEX, 1, state.Theme.text, 2)




