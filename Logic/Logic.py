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