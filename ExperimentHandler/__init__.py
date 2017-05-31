from Experiment import MagTrainExperiment
from appJar import gui
import time, threading, os, sys

'''
The Experiment Thread will run the experiment passed into it
'''
class ExperimentThread(threading.Thread):

    experiment = None
    running = False
    
    def __init__(self, experiment):
        self.experiment = experiment
        threading.Thread.__init__(self)

    def run(self):
        if len(self.experiment.expScript) == 0:
            raise RuntimeError("Experiment Script not loaded")
            return
        for line in self.experiment.expScript:
            if len(line) == 1:
                line[0]()
            else:
                line[0](*line[1:])
            if self.running == False:
                self.experiment.board.stop_board()
                print 'Exp Thread Done'
                return
        print 'Exp Thread Done'
        return

'''
The experiment handler loads the ui and the experiment data
It also handles displaying and exporting the logs
'''
class ExperimentHandler(object):
    
    expType = expTime = numTrial = trialTime = rewardSize = fileLoc = buffer = ""
    app = exp = None
    expThread = None
    outTxt = ""
    mLtoS = 2.36 #Conversion from mL to seconds

#Constructor, loads the experiment and makes the UI
    def __init__(self, expType, expTime, numTrial, buffer, trialTime, rewardSize, speedFactor, fileLoc):
        self.expType = expType
        self.expTime = expTime
        self.numTrial = int(numTrial)
        self.trialTime = trialTime
        self.rewardSize = rewardSize * self.mLtoS
        self.fileLoc = fileLoc
        self.buffer = buffer
        if expType == "Magazine Training":
            self.exp = MagTrainExperiment(self.expTime, self.numTrial, self.trialTime, self.rewardSize, speedFactor, buffer, self)
        self.makeUI()
        
#This function defines the UI
    def makeUI(self):
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

#This starts the UI
    def startUI(self, board):
        self.exp.board = board
        self.app.go()
        
#Sends a message to the textbox
    def WriteToTextBox(self,message):
        self.outTxt += '\n' + message

#Updates the textbox to show the new messages
    def update(self):
        txt = self.app.getTextArea("Output")
        if txt != self.outTxt:
            self.app.clearTextArea("Output")
            self.app.setTextArea("Output", self.outTxt)
            self.app.getTextAreaWidget("Output").yview_moveto(1.0)

#Called when start is pressed, this function starts the experiment
    def StartExperiment(self,name=""):
        self.exp.Load()
        self.exp.trialNum = 1
        self.expThread = ExperimentThread(self.exp)
        self.app.disableButton("Start")
        self.app.enableButton("Stop")
        self.app.disableButton("Export")
        self.outTxt = "Start "+str(self.expType)+":\nParameters:\nExperiment Time: "+str(self.expTime)+"\nBuffer: "+str(self.buffer)+"\nNumber of Trials: "+str(self.numTrial)+"\nTrial Length: "+str(self.trialTime)+"\nReward Size(mL): "+str(self.rewardSize/self.mLtoS)+"\n"
        self.expThread.running = True
        self.expThread.setDaemon(True)
        self.expThread.start()

#When the window is closed the handler will try to close the experiment cleanly
    def Close(self):
        if self.expThread != None:
            if self.expThread.running:
                self.expThread.running = False
        self.exp.quitBoard()
        return True

#When stop is pressed this function stops the experiment
    def StopExperiment(self,name=""):
        self.app.enableButton("Start")
        self.app.disableButton("Stop")
        self.app.enableButton("Export")
        self.expThread.running = False
        #self.expThread.join()

#Writes the log data to a csv file

    def WriteFile(self, name):
        fileName = self.fileLoc
        ext = self.fileLoc.split('.')[-1]
        n = 1
        while os.path.exists(fileName):
            fileName = '.'.join(self.fileLoc.split('.')[:-1]) + '-' + str(n) + '.' + ext
            n += 1
        f = open(fileName, 'w')
        f.write(self.outTxt.replace('\t',','))
        f.close()
        self.app.infoBox("Export Complete", "File exported to: "+fileName)
        
if __name__ == "__main__":
    h = ExperimentHandler("Magazine Training", 30, 3, 1, 5, 1, 1, "./t")
    h.startUI()
    
