from Experiment import MagTrainExperiment, TestExperiment
from appJar import gui
import Tkinter
import time, thread, os

class Handler(object):
    
    expType = expTime = numTrial = trialTime = rewardSize = fileLoc = ""
    app = exp = None
    expThread = None
    outTxt = ""
    
    def __init__(self, expType, expTime, numTrial, trialTime, rewardSize, fileLoc):
        self.expType = expType
        self.expTime = expTime
        self.numTrial = int(numTrial)
        self.trialTime = trialTime
        self.rewardSize = rewardSize
        self.fileLoc = fileLoc
        if expType == "Magazine Training":
            self.exp = MagTrainExperiment(self.expTime, self.numTrial, self.trialTime, self.rewardSize, self)
            self.exp.Load()
        if expType == "Testing":
            self.exp = TestExperiment(self.expTime, self.numTrial, self.trialTime, self.rewardSize, self)
            self.exp.Load()
            
    def startUI(self):
        self.app = gui(self.expType)
        self.app.setGeometry(400,800)
        self.app.addScrolledTextArea("Output")
        self.app.setTextAreaHeight("Output",42)
        self.app.startLabelFrame("Control", 3, 0)
        self.app.addButton("Start", self.StartExperiment, 0,0)
        self.app.addButton("Stop", self.StopExperiment,0,1)
        self.app.addButton("Export", self.WriteFile,0,2)
        self.app.disableButton("Export")
        self.app.stopLabelFrame()
        self.app.setPollTime(1)
        self.app.registerEvent(self.update)
        self.app.go()
        self.StopExperiment()
        
    def WriteToTextBox(self,message):
        self.outTxt += '\n' + message
        self.update()
        
    def update(self):
        txt = self.app.getTextArea("Output")
        if txt != self.outTxt:
            self.app.clearTextArea("Output")
            self.app.setTextArea("Output", self.outTxt)
            self.app.getTextAreaWidget("Output").yview_moveto(1.0)
        
    def StartExperiment(self,name=""):
        self.exp.SetExp(True)
        self.expThread = thread.start_new_thread(self.exp.RunExperiment,())
        self.app.disableButton("Start")
        self.app.enableButton("Stop")
        self.app.disableButton("Export")
        self.outTxt = "Start "+str(self.expType)+":\nParameters:\nExperiment Time: "+str(self.expTime)+"\nNumber of Trials: "+str(self.numTrial)+"\nTrial Length: "+str(self.trialTime)+"\nReward Size: "+str(self.rewardSize)+"\n"
        
    def StopExperiment(self,name=""):
        self.exp.SetExp(False)
        self.app.enableButton("Start")
        self.app.disableButton("Stop")
        self.app.enableButton("Export")
        self.exp.Abort()
        
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
        
#h = Handler("Magazine Training", 1800, 40, 45, 1.0, "./")
#h.startUI()

