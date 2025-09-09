from app.Appdata import Appdata as state
import math
from math import cos, sin, tan, sqrt
from math import radians as rad
from Logic.Logic import pythagorean_distance
from numpy.linalg import norm
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
    aoe_start = np.array([0, 0], dtype=np.int32)
    floating = False
    quit = False
    overlay = None
    aoe_position = np.array([500, 500], dtype=np.int32)


    def __init__(self):
        self.effects = []
        self.type = ""

    def reset(self):
        self.active = False
        self.path = None
        self.st_time = 0
        self.time_set = False
        self.time_set2 = False
        self.resizing = False
        self.size = 0
        self.points = None
        self.aoe_start = np.array([0, 0], dtype=np.int32)
        self.floating = False
        self.quit = False

    def activate_type(self, type):
        self.reset()
        allowlist = ["s", "c", "r", "l", "p"] # will reject other types
        if type not in allowlist:
            raise ValueError(f"The types passed must be in the following allowlist: {allowlist}")
        self.type = type
        self.floating = True
        self.active = True
        self.aoe_start = np.array([0, 0], dtype=np.int32)
    to_move = 0
    def move(self, grab):
        if len(self.effects) == 0:
            print("No effects to move!")
            self.active = False
            self.type = ""
            return False
        if not self.floating and grab:
            least = 999_999
            for ite, eff in enumerate(self.effects):
                dist = norm(state.pointer - eff[1])
                if dist < least:
                    self.to_move = ite
                    least = dist
            self.floating = True
            if least == 999_999:
                self.active = False
                self.type = ""
                print("No movable effect! Path objects can not be moved")
                return False

        if grab and self.floating:
            vect = self.effects[self.to_move][2] - self.effects[self.to_move][1]
            self.effects[self.to_move][1] = state.pointer
            if self.effects[self.to_move][0] != "s":
                self.effects[self.to_move][2] = state.pointer + vect
        if not grab and self.floating:
            self.active = False
            self.once = False
            self.floating = False
            self.type = ""
        cv2.circle(self.overlay, state.pointer, 10, state.Theme.pointer, -1)



    def assign_cv2(self, cv2_obj):
        """to prevent circular import the cv2 object is set using this function"""
        self.cv2_obj = cv2_obj

    def add_effect(self, effect):
        # effect should be: (kind, position, size) or (kind, start, end)
        # The effect may also be the type and a class object, like the pathing object
        self.effects.append(effect)

    def draw(self):
        if self.quit:
            exit()
        if self.active:
            color = state.Theme.active
        elif not self.active:
            color = state.Theme.passive
        for eff in self.effects:
            if eff[0] == "s":
                self.cv2_obj.circle(self.overlay, eff[1], eff[2], color, 5)
            if eff[0] == "l":
                self.cv2_obj.line(self.overlay, eff[1], eff[2], color, 10)
            if eff[0] == "c":
                points = self.generate_cone(eff[1], eff[2])
                self.cv2_obj.polylines(self.overlay, np.int32([points]), True, color, 5)
            if eff[0] == "r":
                points = self.generate_square(eff[1], eff[2])
                self.cv2_obj.polylines(self.overlay, np.int32([points]), True, color, 5)
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
            if dist < least and eff[0] != "p":
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
                self.aoe_start = self.aoe_position
                if self.type == "d":
                    aoe_man.delete_nearest(state.pointer)
                    self.type = ""
                    self.active = False

            elif self.floating:
                cv2.ellipse(self.overlay, state.pointer, (30, 30), 0, 0, del_t / 0.4 * 360, state.Theme.pointer, -1)
            self.aoe_size = int(round((10 + norm(state.pointer - self.aoe_position) / 2) / 5
                                       ,-1) * 5 * state.fcal)

        elif self.floating:
            self.aoe_position = state.pointer
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
                    aoe_man.add_effect([self.type, self.aoe_position, int(self.size/state.fcal)])
                if self.type == "l":
                    aoe_man.add_effect([self.type, self.aoe_start, end])
                if self.type == "c":
                    aoe_man.add_effect([self.type, self.aoe_start, end])
                if self.type == "r":
                    aoe_man.add_effect([self.type, self.aoe_start, end])
                if self.type == "p":
                    aoe_man.add_effect((self.type, self.path))
                    self.path = None
                self.active = False
                self.once = False
            else:
                cv2.ellipse(self.overlay, state.pointer, (30, 30), 0, 0, del_t / 0.4 * 360, state.Theme.pointer, -1)

        if self.type == "s":

            self.size = int(round(norm(self.aoe_position - state.pointer) * state.fcal / 5, -0) * 5)
            cv2.circle(self.overlay, self.aoe_position, int(self.size/state.fcal), state.Theme.active, 5)
            cv2.putText(self.overlay, str(self.size) + "ft",
                        [self.aoe_position[0] + 80, self.aoe_position[1] + 80],
                        cv2.FONT_HERSHEY_SIMPLEX, 1, state.Theme.text, 2)
        if self.type == "c" and not self.floating:
            if self.resizing:
                self.points = self.generate_cone(self.aoe_start, state.pointer)
                end = state.pointer
            cv2.polylines(self.overlay, np.int32([self.points]), True, state.Theme.active, 5)
            size = round((10 + pythagorean_distance(
                self.aoe_start[0], self.aoe_start[1], end[0], end[1])) * state.fcal / 5,-0) * 5

            cv2.putText(self.overlay, str(size) + "ft",
                        [self.aoe_position[0] + 80, self.aoe_position[1] + 80],
                        cv2.FONT_HERSHEY_SIMPLEX, 1, state.Theme.text, 2)
        if self.type == "r" and not self.floating:
            if self.resizing:
                self.points = self.generate_square(self.aoe_start, state.pointer)
                end = state.pointer
            size = round(
                (10 + pythagorean_distance(self.aoe_start[0], self.aoe_start[1], end[0], end[1])) * state.fcal / 5,
                -0) * 5
            cv2.polylines(self.overlay, np.int32([self.points]), True, state.Theme.active, 5)
            cv2.putText(self.overlay, str(size) + "ft",
                        [self.aoe_position[0] + 80, self.aoe_position[1] + 80],
                        cv2.FONT_HERSHEY_SIMPLEX, 1, state.Theme.text, 2)
        if self.type == "l" and not np.all(self.aoe_start == 0):
            if self.resizing:
                end = self.generate_line(self.aoe_start, state.pointer)
            cv2.line(self.overlay, self.aoe_start, end, state.Theme.active, 10)
            size = round(
                (10 + pythagorean_distance(self.aoe_start[0], self.aoe_start[1], end[0], end[1])) * state.fcal,
                -1)
            cv2.putText(self.overlay, str(size) + "ft", [self.aoe_position[0] + 80, self.aoe_position[1] + 80],
                        cv2.FONT_HERSHEY_SIMPLEX, 1, state.Theme.text, 2)
        cv2.circle(self.overlay, state.pointer, 10, state.Theme.pointer, -1)
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
        self.path = [np.array(start, dtype=np.int32)]
        self.dist = 0

    def add_point(self, point):
        """adds points to the pathing object, strictly in 5 foot steps
        """
        point = np.array(point, dtype=np.int32)
        dist = norm(point-self.path[-1]) * state.fcal
        if dist >= 5:
            gen_point = np.round(self.path[-1] + (point - self.path[-1])/dist * 5)
            self.path.append(np.array(gen_point, dtype=np.int32))
            self.dist += round(norm(self.path[-2]-self.path[-1])*state.fcal)

    def draw(self, active):
        if active:
            color = state.Theme.active
        elif not active:
            color = state.Theme.passive
        self.cv2_obj.polylines(aoe_man.overlay, np.int32([self.path]), False, color, 5)
        self.cv2_obj.putText(aoe_man.overlay, str(self.dist) + "ft", self.path[-1], cv2.FONT_HERSHEY_SIMPLEX, 1, state.Theme.text, 2)




aoe_man = aoe_manager()