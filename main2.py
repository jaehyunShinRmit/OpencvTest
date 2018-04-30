import queue
import sys
import threading
import time

import cv2
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from PyQt5.uic import loadUi
import serial

from serialThreadFile import serialThreadClass


class FrambotUI(QDialog):
    def __init__(self):
        super(FrambotUI, self).__init__()
        loadUi('FrambotUI.ui', self)
        self.image = None
        self.image1 = None
        self.processedImage = None
        self.Enabled = False
        self.capture = None
        self.capture1 = None
        self.Save1 = False
        self.out = None
        self.out1 = None
        self.port = 'COM4'
        self.port_2 = 'COM6'
        self.isPort1connected = False
        self.isPort2connected = False
        self.feedstartButton.clicked.connect(self.feedstart)
        self.feedendButton.clicked.connect(self.feedend)
        self.feedstartButton_2.clicked.connect(self.feedstart_2)
        self.feedendButton_2.clicked.connect(self.feedend_2)
        self.startButton.clicked.connect(self.start_webcam)  ## add function ID
        self.stopButton.clicked.connect(self.stop_webcam)
        self.processButton.toggled.connect(self.process)
        self.saveButton.clicked.connect(self.savevideo)
        self.processButton.setCheckable(True)
        self.sendButton.clicked.connect(self.sendmsg)
        self.sendButton_2.clicked.connect(self.sendmsg_2)
        self.comportBox.activated.connect(self.update_comport)
        self.comportBox_2.activated.connect(self.update_comport_2)
        self.mySerial = serialThreadClass()
        self.mySerial_2 = serialThreadClass()
        self.mySerial.msg.connect(self.textEdit.append)
        self.mySerial_2.msg.connect(self.textEdit_2.append)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

        if e.key() == Qt.Key_Up:
            print('up')
            msg = 'U'
        elif e.key() == Qt.Key_Down:
            print('Down')
            msg = 'D'
        elif e.key() == Qt.Key_Left:
            print('Left')
            msg = 'L'
        elif e.key() == Qt.Key_Right:
            print('Right')
            msg = 'R'
        if self.isPort1connected:
            self.mySerial.sendSerial(msg)
            print(msg + 'has been sent')

    def feedend_2(self):
        self.mySerial_2.terminate()
       #self.mySerial.close()  # run thread for re

    def feedstart_2(self):
        try:
            self.mySerial_2.open()
            self.mySerial_2.start()  # run thread for re
            self.isPort2connected = True
        except serial.SerialException:
            print('Failed to open Comport.')

    def update_comport_2(self, index):
        self.port_2 = self.comportBox_2.currentText()
        self.mySerial_2.updateport(self.port_2)
        print('Current comport is :' + self.comportBox.currentText())

    def sendmsg_2(self):
        msg_2 = self.lineEdit_2.text()
        print(msg_2)
        self.setFocus()
        self.mySerial_2.sendSerial(msg_2)

    def feedend(self):
        self.mySerial.terminate()
       #self.mySerial.close()  # run thread for re

    def feedstart(self):
        try:
            self.mySerial.open()
            self.mySerial.start()  # run thread for re
            self.isPort1connected = True
        except serial.SerialException:
            print('Failed to open Comport.')


    def update_comport(self, index):
        self.port = self.comportBox.currentText()
        self.mySerial.updateport(self.port)
        print('Current comport is :' + self.comportBox.currentText())

    def sendmsg(self):
        msg = self.lineEdit.text()
        self.setFocus()
        print(msg)
        self.mySerial.sendSerial(msg)


    def savevideo(self):

        if self.Save1:
            self.Save1 = False
            self.out.release()
            self.out1.release()
        else:
            self.Save1 = True
            self.out = cv2.VideoWriter('outpy.wma', cv2.VideoWriter_fourcc('W', 'M', 'V', '1'), 30, (640, 480))
            self.out1 = cv2.VideoWriter('outpy1.wma', cv2.VideoWriter_fourcc('W', 'M', 'V', '1'), 30, (640, 480))
            print('save button pressed')

    def process(self, status):
        if status:
            self.Enabled = True
            self.processButton.setText('Process Stop')
            msg = 'K12 D1'
            self.mySerial.sendSerial(msg)
            self.savevideo()
        else:
            self.Enabled = False
            self.processButton.setText('Process Start')
            self.out.release()
            self.out1.release()

    def start_webcam(self):
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

        self.capture1 = cv2.VideoCapture(1)
        self.capture1.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.capture1.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  ## call update_frame function every 5ms


    def update_frame(self):
        ret, self.image = self.capture.read()
        self.image = cv2.flip(self.image, 1)
        self.displyImage(self.image, 1)

        ret1, self.image1 = self.capture1.read()
        self.image1 = cv2.flip(self.image1, 1)
        self.displyImage(self.image1, 2)

        if self.Save1:
            self.out.write(self.image)
            self.out1.write(self.image1)

    def stop_webcam(self):
        self.timer.stop()

    def displyImage(self, img, window=1):

        qformat = QImage.Format_Indexed8

        if len(img.shape) == 3:  # [0]=rows, [1]=cols [2]=channels
            if (img.shape[2]) == 4:
                qformat = QImage.Format_RGBA8888
                print('RGBA')
            else:
                qformat = QImage.Format_RGB888
                #print('RGB')
        outImage = QImage(img, img.shape[1], img.shape[0], img.strides[0], qformat)
        # BGR -> RGB
        outImage = outImage.rgbSwapped()

        if window == 1:
            self.imgLabel.setPixmap(QPixmap.fromImage(outImage))
            self.imgLabel.setScaledContents(True)

        if window == 2:
            self.imgLabel2.setPixmap(QPixmap.fromImage(outImage))
            self.imgLabel2.setScaledContents(True)

app = QApplication(sys.argv)
window = FrambotUI()
window.setWindowTitle('Frambot UI test')
# window.setGeometry(100,100,400,200)
window.show()
window.setFocus()
sys.exit(app.exec_())

