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
        self.index= 0
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
        self.pushButton_Up.clicked.connect(self.advance)
        self.pushButton_Down.clicked.connect(self.retreat)
        self.pushButton_Left.clicked.connect(self.turn_left)
        self.pushButton_Right.clicked.connect(self.turn_right)
        self.feedstartButton.clicked.connect(self.feed_start)
        self.feedendButton.clicked.connect(self.feed_end)
        self.feedstartButton_2.clicked.connect(self.feed_start_2)
        self.feedendButton_2.clicked.connect(self.feed_end_2)
        self.startButton.clicked.connect(self.start_webcam)  ## add function ID
        self.stopButton.clicked.connect(self.stop_webcam)
        self.indexButton.clicked.connect(self.index_up)
        self.indexDownButton.clicked.connect(self.index_down)
        self.saveButton.clicked.connect(self.save_video)
        self.sendButton.clicked.connect(self.send_msg)
        self.sendButton_2.clicked.connect(self.send_msg_2)
        self.comportBox.activated.connect(self.update_comport)
        self.comportBox_2.activated.connect(self.update_comport_2)
        self.mySerial = serialThreadClass()
        self.mySerial_2 = serialThreadClass()
        self.mySerial.msg.connect(self.textEdit.append)
        self.mySerial_2.msg.connect(self.textEdit_2.append)

    def advance(self):
        """
        Sending Msg to Arudino for advance

        """
        msg = 'K11 D2'
        try:
            self.mySerial.sendSerial(msg)
        except serial.SerialException:
            print('Port1 - Failed to send a message ')

    def retreat(self):
        msg = 'K13 D2'
        try:
            self.mySerial.sendSerial(msg)
        except serial.SerialException:
            print('Port1 - Failed to send a message ')

    def turn_left(self):
        msg = 'K14 D2'
        try:
            self.mySerial.sendSerial(msg)
        except serial.SerialException:
            print('Port1 - Failed to send a message ')

    def turn_right(self):
        msg = 'K15 D2'
        try:
            self.mySerial.sendSerial(msg)
        except serial.SerialException:
            print('Port1 - Failed to send a message ')

    def feed_end_2(self):
        self.mySerial_2.terminate()

    def feed_start_2(self):
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

    def send_msg_2(self):
        try:
            msg_2 = self.lineEdit_2.text()
            # self.setFocus() # For keyboard control
            self.mySerial_2.sendSerial(msg_2)
        except serial.SerialException:
            print('Port2 - Failed to send a message ')

    def feed_end(self):
        self.mySerial.terminate()

    def feed_start(self):
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

    def send_msg(self):
        try:
            msg = self.lineEdit.text()
            # self.setFocus() # For keyboard control
            self.mySerial.sendSerial(msg)
        except serial.SerialException:
            print('Port1 - Failed to send a message ')

    def save_video(self):
        # Save Data Button
        if self.Save1:
            self.Save1 = False
            self.out.release()
            self.out1.release()
            print('Stop Saving')
        else:
            ##Create video file name
            localtime = time.localtime(time.time())
            if localtime.tm_min < 10:
                minuteWithZero = '0' + str(localtime.tm_min)
            else:
                minuteWithZero =  str(localtime.tm_min)

            video1 = 'FrontView_' + str(localtime.tm_hour) + minuteWithZero + str(localtime.tm_sec) + '.wma'
            video2 = 'TopView_' + str(localtime.tm_hour) + minuteWithZero + str(localtime.tm_sec) + '.wma'

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
            header = ['Index','FrontImageName', 'TopImageName', 'FrontBack1', 'FrontBack2', 'LeftRight1', 'LeftRigh2',
                      'ax(ms2)', 'ay(ms2)', 'az(ms2)','gx(rad/s)','gy(rad/s)','gz(rad/s)',
                      'mx(nT)','my(nT)','mz(nT)', 'latitude' ,'longitude','altitude','Heading(IMU(rad))','Heading(GPS)']
            with myFile:
                self.writer = csv.writer(myFile)
                self.writer.writerow(header)
            try:
                self.out = cv2.VideoWriter(video1, cv2.VideoWriter_fourcc('W', 'M', 'V', '1'), 30, (640, 480))
                self.out1 = cv2.VideoWriter(video2, cv2.VideoWriter_fourcc('W', 'M', 'V', '1'), 30, (640, 480))
                print('Video Recorders have been created')
                # preparing saving. The image data are saved in update_frame()
                self.Save1 = True
            except cv2.error:
                print('Failed to create Camera has not been initiated')

    def index_up(self):
        """
        update index
        used in go-stop-go testing
        used in initial soil sensor testing
        :return:
        """
        self.index = self.index + 1
        self.indexButton.setText(str(self.index))

    def index_down(self):
        """
        decrease index
        used in go-stop-go testing
        used in initial soil sensor testing
        :return:
        """
        self.index = self.index - 1
        self.indexButton.setText(str(self.index))

    def start_webcam(self):
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

        self.capture1 = cv2.VideoCapture(1)
        self.capture1.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.capture1.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(200)  #call update_frame function every 200ms 5hz

    def update_frame(self):
        # 1. Update frame for both cameras
        # 2. Capture images when required
        # 3. Record videos when required
        try:
            ret, self.image = self.capture.read()
        except cv2.error:
            print('Failed to capture images from Camera0')
        self.image = cv2.flip(self.image, 1)
        self.disply_image(self.image, 1)

        try:
            ret1, self.image1 = self.capture1.read()
        except cv2.error:
            print('Failed to capture images from Camera1')
        self.image1 = cv2.flip(self.image1, 1)
        self.disply_image(self.image1, 2)

        if self.Save1:
            a = self.mySerial.getmsgstr()
            b = a[2:-5]  #Remove b' at the Front and /r/n at the End
            msg_list=b.split(',')
            threshold = (int(msg_list[0]) + int(msg_list[1])) / 2
            if threshold> 140.0: ##save image and data only robot is moving forward.
                self.ImageNumber = self.ImageNumber + 1 #number of image captured
                front_image_name = 'FrontImage' + str(self.ImageNumber)
                top_image_name   = 'TopImage' + str(self.ImageNumber)
                front_image_path = os.path.join(self.path, front_image_name) + '.png'
                top_image_path   = os.path.join(self.path, top_image_name) + '.png'
                csv_out  = str(self.index) + ',' + front_image_name + ',' + top_image_name + ',' + b
                my_list  = csv_out.split(',') # Imagename1 Imagename2 L/R1 L/R2 F/B1 F/B2 Roll Pitch Heading
                csv_name = os.path.join(self.path, 'Data.csv')
                myFile   = open(csv_name, 'a+', newline='')
                with myFile:
                    self.writer = csv.writer(myFile)
                    self.writer.writerow(my_list)
                cv2.imwrite(front_image_path, self.image) #save png Image
                cv2.imwrite(top_image_path, self.image1)  #save png Image
                #Save Video
                self.out.write(self.image)
                self.out1.write(self.image1)

    def stop_webcam(self):
        self.timer.stop()

    def disply_image(self, img, window=1):

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
