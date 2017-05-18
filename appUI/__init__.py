from appJar import gui
from ExperimentHandler import ExperimentHandler
import os, pickle

"""
This class defines the initial GUI
The GUI allows a user to change settings and pick an experiment to run
"""

class GUI(object):
    app = None #Contains the appJar object
    handler = None #Contains the experiment handler to be loaded
    fields = types = [] #Fields is an array that defines the text boxes on the gui
                        #Types defines the experiment types
    title = ""          #The title of the window
    exitCode = -1       #Should be set to 0 if there were no errors
    defaults = {}       #Default options to bo loaded from op.def
    hardDefaults = {    #Hard coded defaults to be used if op.def is not found
        'Length of Trial (s)':30.0,
        'Buffer (s)':15.0,
        'Reward Size (s)':1.0,
        'Speed Factor':1.0,
        'File Location':os.getcwd()+"/test.csv",
        'Length of Experiment (s)':1800.0,
        'Number of Trials':40.0
        }

    def resetDefaults(self,name):
        for field in self.fields:
            self.app.setEntry(field[0], self.hardDefaults[field[0]])
        self.update()

    def saveDefaults(self, path = "./op.def"):
        for field in self.fields:
            self.defaults[field[0]] = self.app.getEntry(field[0])
        with open(path, 'w') as f:
            pickle.dump(self.defaults, f, 0)
        return

    def loadDefaults(self, path = "./op.def"):
        if os.path.exists(path):
            with open(path, 'r') as f:
                self.defaults = pickle.load(f)

        return    

    def getTestType(self):
        return self.app.getRadioButton("expType")
    
    #Runs when the start button is pressed
    def start(self,name):
        self.saveDefaults()
        self.app.stop()
        if self.getTestType() == "Camera Test":
            from Camera import CameraHandler
            self.handler = CameraHandler()
        elif self.getTestType() == "Control":
            from Control import ControllerHandler
            self.handler = ControllerHandler()
        else:
            self.handler = ExperimentHandler(self.app.getRadioButton("expType"), *[self.app.getEntry(field[0]) for field in self.fields])
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
        startEn = True  
        for field in self.fields:
            startEn = startEn and (len(str(self.app.getEntry(field[0]))) > 0)
            
        expLen = float(self.app.getEntry(self.fields[0][0]))
        numTri = float(self.app.getEntry(self.fields[1][0]))
        buffer = float(self.app.getEntry(self.fields[2][0]))
        reward = float(self.app.getEntry(self.fields[4][0]))
        if numTri == 0:
            triLen = 0
            startEn = False
        else:
            triLen = expLen / numTri - buffer - reward
        if triLen <= 0:
            startEn = False
            
        self.app.setEntry(self.fields[3][0],str(triLen))

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
        self.loadDefaults()
        self.title = "Operant Conditioning"
        self.types = ["Magazine Training","Camera Test","Control"]
        self.fields = [
            ["Length of Experiment (s)","num","1800",True], 
            ["Number of Trials","num", "40",True],
            ["Buffer (s)", "num", "15", True],
            ["Length of Trial (s)","num","45",False], 
            ["Reward Size (s)","num", "1",True],
            ["Speed Factor", "num", "1.0", True],
            ["File Location", "txt", os.getcwd()+"/test.csv",True]
        ]
        if len(self.defaults) > 0:
            for field in self.fields:
                if field[0] in self.defaults.keys():
                    field[2] = self.defaults[field[0]]

    def __exit__(self,*err):
        return True

    def __enter__(self):
        return self

    def startGUI(self):
        self.app = gui(self.title)
        #Left Side
        self.app.startLabelFrame("Experiment Type", 0,0)
        self.app.setSticky("n")
        self.app.setInPadding(0,10)
        for expType in self.types:
            self.app.addRadioButton("expType", expType)
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
                self.app.getEntryWidget(field[0]).bind("<KeyRelease>",self.update)
            if field[3] == False:
                self.app.disableEntry(field[0])
        self.app.addButton("Browse...",self.browse)
        self.app.stopLabelFrame()
        #Bottom
        self.app.addButton("Reset to Defaults", self.resetDefaults, 1, )
        self.app.addButton("Start", self.start, 1, 1)
        self.app.addButton("Cancel", quit, 1, 2)
        self.update()
        self.app.go()
