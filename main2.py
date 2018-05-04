import queue
import sys
import threading
import time
import os
import cv2
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from PyQt5.uic import loadUi
import serial
import csv

from serialThreadFile import serialThreadClass


class FrambotUI(QDialog):
    def __init__(self):
        super(FrambotUI, self).__init__()
        loadUi('FrambotUI.ui', self)
        self.image = None
        self.image1 = None
        self.writer = None
        self.processedImage = None
        self.path = None
        self.ImageNumber = 0
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

    # def keyPressEvent(self, e):
    #     if e.key() == Qt.Key_Escape:
    #         self.close()
    #
    #     if e.key() == Qt.Key_Up:
    #         print('up')
    #         msg = 'U'
    #     elif e.key() == Qt.Key_Down:
    #         print('Down')
    #         msg = 'D'
    #     elif e.key() == Qt.Key_Left:
    #         print('Left')
    #         msg = 'L'
    #     elif e.key() == Qt.Key_Right:
    #         print('Right')
    #         msg = 'R'
    #     if self.isPort1connected:
    #         self.mySerial.sendSerial(msg)
    #         print(msg + 'has been sent')

    def feedend_2(self):
        self.mySerial_2.terminate()

    def feedstart_2(self):
        try:
            self.mySerial_2.open()
            self.mySerial_2.start()  # run thread
            self.isPort2connected = True
        except serial.SerialException:
            print('Failed to open Comport.')

    def update_comport_2(self, index):
        self.port_2 = self.comportBox_2.currentText()
        self.mySerial_2.updateport(self.port_2)
        print('Current port for comport2 is :' + self.comportBox.currentText())

    def sendmsg_2(self):
        try:
            msg_2 = self.lineEdit_2.text()
            # self.setFocus() # For keyboard control
            self.mySerial_2.sendSerial(msg_2)
        except serial.SerialException:
            print('Port2 - Failed to send a message ')

    def feedend(self):
        self.mySerial.terminate()

    def feedstart(self):
        try:
            self.mySerial.open()
            self.mySerial.start()  # run thread
            self.isPort1connected = True
        except serial.SerialException:
            print('Failed to open Comport.')

    def update_comport(self, index):
        self.port = self.comportBox.currentText()
        self.mySerial.updateport(self.port)
        print('Current port for comport1 is :' + self.comportBox.currentText())

    def sendmsg(self):
        try:
            msg = self.lineEdit.text()
            # self.setFocus() # For keyboard control
            self.mySerial.sendSerial(msg)
        except serial.SerialException:
            print('Port1 - Failed to send a message ')

    def savevideo(self):
        # Save Data Button
        if self.Save1:
            self.Save1 = False
            self.out.release()
            self.out1.release()
            print('Stop Saving')
        else:
            ##Create video file name
            localtime = time.localtime(time.time())
            video1 = 'FrontView_' + str(localtime.tm_hour) + str(localtime.tm_min) + str(localtime.tm_sec) + '.wma'
            video2 = 'TopView_' + str(localtime.tm_hour) + str(localtime.tm_min) + str(localtime.tm_sec) + '.wma'

            ##Create path, directory for saving
            directory = str(localtime.tm_hour) + str(localtime.tm_min) + str(localtime.tm_sec)
            self.path = os.path.join(os.getcwd(), directory)
            video1 = os.path.join(self.path, video1)
            video2 = os.path.join(self.path, video2)
            csvName = os.path.join(self.path, 'Data.csv')
            if not os.path.exists(self.path):
                os.makedirs(self.path)
            ##Write Header for CSV file
            myFile = open(csvName, 'w+', newline='')
            header = ['FrontImageName', 'TopImageName', 'Left/Right1', 'Left/Right2', 'Front/Back1', 'Front/Back2',
                      'Roll(rad)', 'Pitch(rad)', 'Heading(rad)']
            with myFile:
                self.writer = csv.writer(myFile)
                self.writer.writerow(header)
            #preparing saving. The image data are saved in update_frame()
            self.Save1 = True
            try:
                self.out = cv2.VideoWriter(video1, cv2.VideoWriter_fourcc('W', 'M', 'V', '1'), 30, (640, 480))
                self.out1 = cv2.VideoWriter(video2, cv2.VideoWriter_fourcc('W', 'M', 'V', '1'), 30, (640, 480))
                print('Video Recorders have been created')
            except:
                print('Failed to create Camera has not been initiated')

    def process(self, status):
        # Move and Capture Button
        if status:
            self.Enabled = True
            self.processButton.setText('Recording')
            msg = 'K12 D20'
            try:
                self.mySerial.sendSerial(msg)
                self.savevideo()
            except serial.SerialException:
                print('Port1 - Failed to send a message ')
        else:
            self.Enabled = False
            self.processButton.setText('Stop')
            self.out.release()
            self.out1.release()

    def start_webcam(self):
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

        self.capture1 = cv2.VideoCapture(0)
        self.capture1.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.capture1.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(100)  #call update_frame function every 10ms

    def update_frame(self):
        # 1. Update frame for both cameras
        # 2. Capture images when required
        # 3. Record videos when required
        ret, self.image = self.capture.read()
        self.image = cv2.flip(self.image, 1)
        self.displyImage(self.image, 1)

        ret1, self.image1 = self.capture1.read()
        self.image1 = cv2.flip(self.image1, 1)
        self.displyImage(self.image1, 2)

        if self.Save1:
            a = self.mySerial.getmsgstr()
            b = a[2:-5]  #Remove b' at the Front and /r/n at the End
            self.ImageNumber = self.ImageNumber + 1 #number of image captured
            front_image_name = 'FrontImage' + str(self.ImageNumber)
            top_image_name = 'TopImage' + str(self.ImageNumber)
            front_image_path = os.path.join(self.path, front_image_name) + '.png'
            top_image_path = os.path.join(self.path, top_image_name) + '.png'
            csvout = front_image_name + ',' + top_image_name + ',' + b
            mylist = csvout.split(',') # Imagename1 Imagename2 L/R1 L/R2 F/B1 F/B2 Roll Pitch Heading
            csv_name = os.path.join(self.path, 'Data.csv')
            myFile = open(csv_name, 'a+', newline='')
            with myFile:
                self.writer = csv.writer(myFile)
                self.writer.writerow(mylist)
            cv2.imwrite(front_image_path, self.image) #save png Image
            cv2.imwrite(top_image_path, self.image1)  #save png Image
            #Save Video
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
                # print('RGB')
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
