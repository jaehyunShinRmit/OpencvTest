import queue
import sys
import threading
import time

from usbCam import FPS
from usbCam import WebcamVideoStream
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from PyQt5.uic import loadUi
import serial
import argparse
import imutils
import cv2

from serialThreadFile import serialThreadClass

ap = argparse.ArgumentParser()
ap.add_argument("-n", "--num-frames", type=int, default=1000,
                help="# of frames to loop over for FPS test")
ap.add_argument("-d", "--display", type=int, default=-1,
                help="Whether or not frames should be displayed")
args = vars(ap.parse_args())

# self.capture = cv2.VideoCapture(0)
# self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#
# self.capture1 = cv2.VideoCapture(1)
# self.capture1.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# self.capture1.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

# created a *threaded* video stream, allow the camera sensor to warmup,
# and start the FPS counter
print("[INFO] sampling THREADED frames from webcam...")
vs = WebcamVideoStream(src=2).start()
fps = FPS().start()

vs2 = WebcamVideoStream(src=0).start()
fps2 = FPS().start()

# loop over some frames...this time using the threaded stream
while fps._numFrames < args["num_frames"]:
    # grab the frame from the threaded video stream and resize it
    # to have a maximum width of 400 pixels
    frame = vs.read()
    frame = imutils.resize(frame, width=400)

    frame2 = vs2.read()
    frame2 = imutils.resize(frame2, width=400)
    # check to see if the frame should be displayed to our screen
    cv2.imshow("Frame", frame)
    cv2.imshow("Frame2", frame2)
    key = cv2.waitKey(1) & 0xFF

    # update the FPS counter
    fps.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()