from appJar import gui
from ExperimentHandler import Handler
import os
    
class GUI(object):
    app = None
    handler = None
    fields = types = []
    title = ""
    exitCode = -1
    #Runs when the start button is pressed
    def start(self,name):
        self.app.stop()
        self.handler = Handler(self.app.getRadioButton("expType"), self.app.getEntry(self.fields[0][0]), self.app.getEntry(self.fields[1][0]), int(self.app.getEntry(self.fields[2][0])), self.app.getEntry(self.fields[3][0]), self.app.getEntry(self.fields[4][0]))
        self.exitCode = 0
    #Disables the start button
    def disableStart(self,):
        self.app.disableButton("Start")
        self.app.disableEnter()
        
    #Enables the start button
    def enableStart(self,):
        self.app.enableButton("Start")
        self.app.enableEnter(self.start)
    
    #Updates the GUI, this should be called after any change to the text fields
    def update(self,name="default"):
        #TODO Trial Length should be >= 15s
        startEn = True
        
        expLen = int(self.app.getEntry(self.fields[0][0]))
        numTri = int(self.app.getEntry(self.fields[1][0]))
        if numTri == 0:
            triLen = 0
        else:
            triLen = expLen // numTri
        self.app.setEntry(self.fields[2][0],str(triLen))
        if triLen < 15:
            startEn = False
            self.app.setEntry(self.fields[2][0],"Should be > 15. Is "+str(triLen))
        
        for field in self.fields:
            startEn = startEn and (len(str(self.app.getEntry(field[0]))) > 0)
        if not startEn:
            self.disableStart()
        else:
            self.enableStart()
        
    #Allows a path to be selected to store the csv
    def browse(self,name):
        path = self.app.saveBox(fileExt=".csv")
        self.app.setEntry(self.fields[4][0], path)
        self.update()
        
    def __init__(self):
        self.title = "Operant Conditioning"
        self.types = ["Magazine Training"]
        self.fields = [
            ["Length of Experiment (s)","num","1800",True], 
            ["Number of Trials","num", "40",True],
            ["Length of Trial (s)","txt","45",False], 
            ["Reward Size (L)","num", "1",True],
            ["File Location", "txt", os.getcwd()+"/test.csv",True]
        ]
        
    def startGUI(self):
        
        self.app = gui(self.title)
        #Left Side
        self.app.startLabelFrame("Experiment Type", 0,0)
        self.app.setSticky("n")
        self.app.setInPadding(0,10)
        for expType in self.types:
            self.app.addRadioButton("expType", expType)
            self.app.addRadioButton("expType", "Testing")
        self.app.stopLabelFrame()
        #Right Side
        self.app.startLabelFrame("Settings", 0,1)
        self.app.setSticky("e")
        for field in self.fields:
            if field[1] == "num":
                self.app.addLabelNumericEntry(field[0])
                self.app.setEntry(field[0],field[2])
                self.app.getEntryWidget(field[0]).bind("<KeyRelease>",self.update)
            elif field[1] == "txt":
                self.app.addLabelEntry(field[0])
                self.app.setEntry(field[0],field[2])
                self.app.getEntryWidget(field[0]).bind("<KeyPress>",self.update)
            if field[3] == False:
                self.app.disableEntry(field[0])
        self.app.addButton("Browse...",self.browse)
        self.app.stopLabelFrame()
        #Bottom
        self.app.addButton("Start", self.start, 1, 0)
        self.app.addButton("Cancel", quit, 1, 1)
        self.update()
        self.app.go()
