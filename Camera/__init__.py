import RPi.GPIO as GPIO
import time,picamera,io,base64,threading
from Handler import Handler
from appJar import gui

LEDPin = 2

class CameraHandler(Handler):
    cam = app = None
    imgStm = buf1 = io.BytesIO()
    image = ""
    capturing = False
    bufCheck = False
    
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LEDPin,GPIO.OUT)
        self.cam = picamera.PiCamera(led_pin = LEDPin, resolution=(800,600))
        _imgStm = io.BytesIO()
        self.app = gui("Camera Preview")
    
    def startUI(self):
        self.capturing = True
        self.takePicture()
        self.app.addImageData("Image",self.image)
        cap = threading.Thread(target = self.capturePicture)
        cap.start()
        up = threading.Thread(target = self.decodePicture)
        up.start()
        self.app.go()
        self.capturing = False
        return

    def setLights(self,state):
        GPIO.output(LEDPin,state)

    def takePicture(self):
        self.cam.capture(self.imgStm,'gif')
        self.imgStm.seek(0)
        self.image = base64.b64encode(self.imgStm.read())
        self.imgStm.seek(0)
        return

    def capturePicture(self):
        while self.capturing:
            s = None
            if self.bufCheck:
                s = self.imgStm
            else:
                s = self.buf1
            s.seek(0)
            self.cam.capture(s,'gif')
            self.bufCheck = not self.bufCheck
        return

    def decodePicture(self):
        while self.capturing:
            s = None
            if self.bufCheck:
                s = self.imgStm
            else:
                s = self.buf1
            self.image = base64.b64encode(s.read())
            self.app.reloadImageData("Image", self.image)
        return

c = CameraHandler()
c.startUI()
