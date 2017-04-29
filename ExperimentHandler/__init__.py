from Experiment import MagTrainExperiment
from Handler import Handler
from appJar import gui
import Tkinter
import time, threading, os, sys

class ExperimentHandler(Handler):
    
    expType = expTime = numTrial = trialTime = rewardSize = fileLoc = buffer = ""
    app = exp = None
    expThread = None
    outTxt = ""
    
    def __init__(self, expType, expTime, numTrial, buffer, trialTime, rewardSize, speedFactor, fileLoc):
        self.expType = expType
        self.expTime = expTime
        self.numTrial = int(numTrial)
        self.trialTime = trialTime
        self.rewardSize = rewardSize
        self.fileLoc = fileLoc
        self.buffer = buffer
        if expType == "Magazine Training":
            self.exp = MagTrainExperiment(self.expTime, self.numTrial, self.trialTime, self.rewardSize, speedFactor, buffer, self)
            self.exp.Load()
            
    def startUI(self):
        self.app = gui(self.expType)
        self.app.setGeometry(400,970)
        self.app.addScrolledTextArea("Output")
        self.app.setTextAreaHeight("Output",42)
        self.app.startLabelFrame("Control", 3, 0)
        self.app.addButton("Start", self.StartExperiment, 0,0)
        self.app.addButton("Stop", self.StopExperiment,0,1)
        self.app.addButton("Export", self.WriteFile,0,2)
        self.app.disableButton("Stop")
        self.app.disableButton("Export")
        self.app.stopLabelFrame()
        self.app.setPollTime(1)
        self.app.registerEvent(self.update)
        self.app.setStopFunction(self.Close)
        self.app.go()
        
    def WriteToTextBox(self,message):
        self.outTxt += '\n' + message
        
    def update(self):
        txt = self.app.getTextArea("Output")
        if txt != self.outTxt:
            self.app.clearTextArea("Output")
            self.app.setTextArea("Output", self.outTxt)
            self.app.getTextAreaWidget("Output").yview_moveto(1.0)
        
    def StartExperiment(self,name=""):
        self.exp.trialNum = 1
        self.exp.SetExp(True)
        self.expThread = threading.Thread(target = self.exp.RunExperiment)
        self.app.disableButton("Start")
        self.app.enableButton("Stop")
        self.app.disableButton("Export")
        self.outTxt = "Start "+str(self.expType)+":\nParameters:\nExperiment Time: "+str(self.expTime)+"\nBuffer: "+str(self.buffer)+"\nNumber of Trials: "+str(self.numTrial)+"\nTrial Length: "+str(self.trialTime)+"\nReward Size: "+str(self.rewardSize)+"\n"
        self.expThread.start()

    def Close(self):
        try:
            self.exp.SetExp(False)
            self.exp.Abort()
        except AttributeError:
            return True
        return True
        
    def StopExperiment(self,name=""):
        self.exp.SetExp(False)
	self.exp.Abort()
        self.app.enableButton("Start")
        self.app.disableButton("Stop")
        self.app.enableButton("Export")
        
    def WriteFile(self, name):
        fileName = self.fileLoc
        ext = self.fileLoc.split('.')[-1]
        n = 1
        while os.path.exists(fileName):
            fileName = '.'.join(self.fileLoc.split('.')[:-1]) + '-' + str(n) + '.' + ext
            n += 1
        f = open(fileName, 'w')
        f.write(self.outTxt)
        f.close()
        self.app.infoBox("Export Complete", "File exported to: "+fileName)
        
