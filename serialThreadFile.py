import serial
from PyQt5.QtCore import pyqtSignal, QThread
from serial.threaded import LineReader, ReaderThread


class serialThreadClass(QThread):
    msg = pyqtSignal(str)

    def __init__(self, parent=None):
        super(serialThreadClass, self).__init__(parent)
        self.seriport = serial.Serial()
        self.seriport.timeout = 1
        self.seriport.baudrate = 115200
        self.seriport.port = 'COM4'

    def open(self):
        self.seriport.open()

    def updateport(self,newport):
        self.seriport.port = newport

    def run(self):#thread run fnc, rec
        while self.seriport.readable():
            veri = self.seriport.readline()
            self.msg.emit(str(veri))
            print(veri)

    def sendSerial(self,message):
        arr = bytes(message+'\n', 'utf-8')
        self.seriport.write(arr)
        #.seriport.write(b'K61\n') #one byte

