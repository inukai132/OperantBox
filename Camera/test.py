from appJar import gui
from Tkinter import PhotoImage

from threading import Thread
from time import sleep
import Tkinter as tk
import gc,sys,datetime
import multiprocessing as mp

from memory_profiler import profile


class Test(object):
    
    head = data = ""
    res = (800,600)
    color = 0
    img = None
    imgClear = False
    
    @profile
    def shade(self):
        #self.updateObj()
        #print 'shading len '+str(len(self.head+self.data))
        #self.app.reloadImageData("Image",self.head+self.data)
        if self.imgClear:
            self.app.addImageData("Image",self.head+self.data)
            self.imgClear = False
        self.color += 1
        if self.color > 3:
            self.color = 0
            self.app.removeImage("Image")
            gc.collect()
            self.imgClear = True
            return

        print str(self.color)
        label = self.app.getImageWidget("Image")
        label.config(image=None)
        label.image=None
        if self.img != None:
            self.img.__del__()
        self.img = PhotoImage(data=self.head+self.data)
        label.config(image=self.img)
        label.image = self.img  #keep a reference!

        
    def __init__(self):
        self.app = gui("Camera Preview",str(self.res[0]+50)+"x"+str(self.res[1]+50))
        self.app.addImageData("Image","P6 1 1 255\n111")
        self.app.setImageSize("Image", self.res[0],self.res[1])
        self.app.registerEvent(self.shade)
        self.app.setPollTime(1)
        self.head = ' '.join(["P6",str(self.res[0]),str(self.res[1]),"255",""])
        self.data = (str(0)*3+' ')*(self.res[0]*self.res[1])
        


    def uiStart(self):
        self.app.go()
        self.run = False
        
    def updateObj(self):
        print 'updating'
        self.head = ' '.join(["P6",str(self.res[0]),str(self.res[1]),"255",""])
        self.data = (str(0)*3+' ')*(self.res[0]*self.res[1])
        
if __name__ == '__main__':
    print tk.__file__
    t = Test()
    sleep(1)
    t.uiStart()
    
