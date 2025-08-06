from math import sqrt

def pythagorean_distance(x1, y1, x2, y2):
    """
    Simple pythogerian distance between two points
    :param x1: x value of first point
    :param y1: y value of first point
    :param x2: x value of second point
    :param y2: y value of second point
    :return: Distance between points
    """
    return sqrt((x1-x2)**2 + (y1-y2)**2)

def grabbing(ind_tip, thum_tip):
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
    if pythagorean_distance(it_x, it_y, tt_x, tt_y)/1.5 < ref:
        return True
    else:
        return False