from math import sqrt
import cv2
from app.Appdata import Appdata as state
from app.Appdata import load_config, save_config
import numpy as np
import screeninfo
import tkinter as tk
from tkinter import filedialog
from numpy.linalg import norm

def pythagorean_distance(x1, y1, x2, y2):
    """
    This function should be replaced by numpy.linalg.norm
    Simple pythogerian distance between two points
    :param x1: x value of first point
    :param y1: y value of first point
    :param x2: x value of second point
    :param y2: y value of second point
    :return: Distance between points
    """
    return sqrt((x1-x2)**2 + (y1-y2)**2)

def check_squareness(points):
    points = points[0]
    dists = []
    for i in range(len(points)):
        dists.append(norm(points[i]- points[i-1]))
    max, dif = np.max(dists), np.max(dists) - np.min(dists)
    if(dif < max * 0.05):
        return True
    else:
        return False

def calibration(cap):
    """
    This function will open and display the calibration code and uses it to
    attempt to produce a scaling factor.
    At the moment this function does not work reliably
    :param cap: The capture instance that the main code uses (camera
    :return: The calculated calibration ratio
    :rtype: float
    """
    calcode = cv2.imread("calibration_code.png")
    screen = screeninfo.get_monitors()[-1]
    state.scr_h, state.scr_w = screen.height, screen.width
    calcode = cv2.resize(calcode, (state.scr_h, state.scr_h))
    calcode = cv2.convertScaleAbs(calcode, alpha=0.6, beta=0)
    cv2.imshow("calibration", calcode)
    cv2.moveWindow("calibration", state.scr_w, 0)
    qcd = cv2.QRCodeDetector()
    count = 0
    while cap.isOpened():
        ret, cal_frame = cap.read()
        retval, points = qcd.detect(cal_frame)
        if points is not None:
            check_squareness(points)
            calcode = cv2.polylines(calcode, np.int32([points]), True, (0, 0, 255), 2)
            cv2.imshow("calibration", calcode)
            cv2.moveWindow("calibration", state.scr_w, 0)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyWindow("calibration")
            ratio = 1
            break

        if retval:
            if check_squareness(points):
                cv2.destroyWindow("calibration")
                pts = np.int32([points])[0][0]
                ratio = pythagorean_distance(pts[0][0], pts[0][1], pts[2][0], pts[2][1])/5746
                return ratio

    return True

def ask_for_file():
    """
    WORK IN PROGRESS
    This function asks the user to choose a map to use
    :return: The filepath to chosen map
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(
        title="Select an Image File",
        filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp;*.gif;*.tiff")]
    )
    print(file_path)
    return file_path

