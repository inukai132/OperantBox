import RPi.GPIO as GPIO
import Tkinter as tk
import time,picamera,io,base64,threading,binascii,os,gc
from appJar import gui
from subprocess import call

LEDPin = 2

class PPMOut(object):
    header = ""
    col=row = 0
    canvas = None
    data = ""
    def __init__(self,c,w,h):
        self.cols = w
        self.rows = h
        self.canvas = c
        self.header = ' '.join(["P6",str(w),str(h),"255",""])
        self.img = self.canvas.getImageWidget("Image")
        
    def write(self, data):
        self.data = data

    def flush(self):
        self.canvas.setImageData("Image",self.header+self.data)
        
class camThread(threading.Thread):
    camera = window = enc = capturing = memRes = None

    def __init__(self, camera, window):
        self.camera = camera
        self.window = window
        self.enc = PPMOut(self.window,self.camera.resolution[0],self.camera.resolution[1])
        threading.Thread.__init__(self)
        self.capturing = True
        self.setDaemon(True)
        self.memRes = 10

    def run(self):
        while self.capturing:
            try:
                self.camera.capture(self.enc,'rgb',use_video_port=True)
            except TypeError:
                return
            time.sleep(.1)
        print 'Thread Done'
    

class CameraHandler(object):
    cam = app = cap = None
    image = "P6 255 255 255\n"
    bufCheck = True
    outs = []
    res = (640,480)
    framerate = 30
    fileName = ""


    def setFileName(self, fileName):
        ext = fileName.split('.')[-1]
        self.fileName = fileName
        n = 1
        noExt = '.'.join(fileName.split('.')[:-1])
        while os.path.exists(self.fileName):
            self.fileName = noExt + '-' + str(n) + '.' + ext
            n += 1
    
    def __init__(self, fileName):
        self.cam = picamera.PiCamera(led_pin = LEDPin, resolution=self.res, framerate=self.framerate)
        self.setFileName(fileName)
        self.app = gui("Camera Preview",str(self.res[0]+50)+"x"+str(self.res[1]+50))
    
    def startUI(self):
        self.stream = io.BytesIO()
        self.app.addImageData("Image","P6 1 1 255\n111")
        self.app.setImageSize("Image", self.res[0],self.res[1])
        self.cap = camThread(self.cam,self.app)
        self.cap.start()
        self.startCap()
        self.app.setStopFunction(self.end)
        self.app.go()

    def getTempPath(self):
        path = '/'.join(self.fileName.split('/')[:-1])
        name = '__'+self.fileName.split('/')[-1]
        return path+'/'+name

    def startCap(self):
        self.cam.start_recording(self.getTempPath(), format='h264')

    def stopCap(self):
        self.cam.stop_recording()

    def saveData(self):
        os.rename(self.getTempPath(), self.fileName)
        time.sleep(.5)
        cmd = ["ffmpeg","-y","-r",str(30),"-i "+self.fileName,"-vcodec copy",'.'.join(self.fileName.split('.')[:-1])+".mp4"]
        print "Command: "+' '.join(cmd)
        call([' '.join(cmd)],shell=True)
        print "Done writing to file "+'.'.join(self.fileName.split('.')[:-1])+".mp4"
        
            
    def setLights(self,state):
        GPIO.output(LEDPin,state)

    def end(self):
        self.bufCheck = False
        self.cap.capturing = False
        self.cam.stop_recording()
        self.saveData()
        return True


if __name__ == "__main__":
    print 'going'
    c = CameraHandler('./tests/test.h264')
    c.startUI()
