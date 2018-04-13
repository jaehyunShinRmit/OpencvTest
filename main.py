import cv2
import sys
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.uic import loadUi


class FrambotUI(QDialog):
    def __init__(self):
        super(FrambotUI,self).__init__()
        loadUi('FrambotUI.ui',self)
        self.image = None
        self.processedImage = None
        self.Enabled = False
        self.startButton.clicked.connect(self.start_webcam) ## add function ID
        self.stopButton.clicked.connect(self.stop_webcam)
        self.processButton.toggled.connect(self.process)
        self.processButton.setCheckable(True)


    def process(self,status):
        if status:
            self.Enabled = True
            self.processButton.setText('Process Stop')
        else:
            self.Enabled = False
            self.processButton.setText('Process Start')

    def start_webcam(self):
        self.capture=cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH,640)

        self.timer=QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(5) ## call update_frame function every 5ms

    def update_frame(self):
        ret,self.image=self.capture.read()
        self.image=cv2.flip(self.image,1)
        self.displyImage(self.image,1)

        if self.Enabled:
            gray = cv2.cvtColor(self.image,cv2.COLOR_RGB2GRAY) if len(self.image.shape)>=3 else self.image
            self.processedImage=cv2.Canny(gray,100,200)
            self.displyImage(self.processedImage,2)

    def stop_webcam(self):
        self.timer.stop()

    def displyImage(self,img,window=1):
        qformat = QImage.Format_Indexed8

        if len(img.shape)==3: #[0]=rows, [1]=cols [2]=channels
            if(img.shape[2])==4:
                qformat=QImage.Format_RGBA8888
            else:
                qformat=QImage.Format_RGB888
        outImage=QImage(img,img.shape[1],img.shape[0],img.strides[0],qformat)
        #BGR -> RGB
        outImage=outImage.rgbSwapped()

        if window ==1:
            self.imgLabel.setPixmap(QPixmap.fromImage(outImage))
            self.imgLabel.setScaledContents(True)

        if window ==2:
            self.imgLabel2.setPixmap(QPixmap.fromImage(outImage))
            self.imgLabel2.setScaledContents(True)

app = QApplication(sys.argv)
window = FrambotUI()
window.setWindowTitle('Frambot UI test')
#window.setGeometry(100,100,400,200)
window.show()
sys.exit(app.exec_())



# img =cv2.imread('Capture.PNG',1)
# cv2.imshow('Capture',img)
# cv2.waitKey()
# cv2.destroyAllWindows()
