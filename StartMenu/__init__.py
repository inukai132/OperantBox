from appJar import gui
from Experiments.LeverTrain import leverTrain
from Experiments.MagTrain import magTrain
from Experiments.NosePokeTrain import nosePokeTrain

class GUI(object):
    
    app = None              #Contains the appJar object
    handler = None          #Contains the experiment handler to be loaded
    experiments = [magTrain, leverTrain, nosePokeTrain]
    title = ""              #The title of the window
    exitCode = -1           #Should be set to 0 if there were no errors
    
    expTypes = ["Control"]
    
    def __exit__(self,*err):
        return True

    def __enter__(self):
        return self
    
#Constructor, loads the default values or sets the fields to the hard defaults
    def __init__(self):
        self.title = "Operant Conditioning"
        for exp in self.experiments:
            self.expTypes.append(exp.name)
        self.buildGUI()

#This is where the GUI is defined
    def buildGUI(self):
        self.app = gui(self.title)
        self.app.setGeometry(650, 250)
        #Left Side
        self.app.startLabelFrame("Experiment Type", 0,0)
        self.app.setSticky("n")
        self.app.setInPadding(0,10)
        for expType in self.expTypes:
            self.app.addRadioButton("expType", expType)
        self.app.setRadioButtonChangeFunction("expType", self.update)
        self.app.stopLabelFrame()
        #Right Side
        self.app.startLabelFrame("Settings", 0,1)
        self.app.setSticky("e")
        for exp in self.experiments:
            row = 0
            for field in exp.options.itervalues():
                name = exp.name+field.optName
                if field.optType == "num":
                    self.app.addLabel(name+'Lab',field.optName,row,0)
                    self.app.addNumericEntry(name,row,1)
                    self.app.setEntry(name,field.optValue)
                    self.app.getEntryWidget(name).bind("<KeyRelease>",self.update)
                elif field.optType == "txt":
                    self.app.addLabel(name+'Lab',field.optName,row,0)
                    self.app.addEntry(name,row,1)
                    self.app.setEntry(name,field.optValue)
                    self.app.getEntryWidget(name).bind("<KeyRelease>",self.update)
                if not field.optEnabled:
                    self.app.disableEntry(name)
                row += 1
        self.hideAll()
        self.app.stopLabelFrame()
        #Bottom
        self.app.addButton("Start", self.start, 1, 1)
        self.app.addButton("Cancel", quit, 1, 0)
        self.update()
        
#Returns the experiment type    
    def getTestType(self):
        return self.app.getRadioButton("expType")
    
#Runs when the start button is pressed
#Loads the handler, saves the fields, sets the exit code
    def start(self,name):
        #self.saveDefaults()
        self.app.stop()
        if self.getTestType() == "Control":
            from Control import ControllerHandler
            self.handler = ControllerHandler()
            self.exitCode = 0
        else:
            for exp in self.experiments:
                if exp.name == self.getTestType():
                    self.handler = exp
                    self.exitCode = 0
                    break
        
#Disables the start button
    def disableStart(self):
        self.app.disableButton("Start")
        self.app.disableEnter()
        
#Enables the start button
    def enableStart(self):
        self.app.enableButton("Start")
        self.app.enableEnter(self.start)
    
#Updates the GUI, this should be called after any change to the text fields
    def update(self,name="default"):
        selTest = self.getTestType()
        self.hideAll()
        for exp in self.experiments:
            if exp.name == selTest:
                for field in exp.options.itervalues():
                    name = exp.name+field.optName
                    self.app.showEntry(name)
                    self.app.showLabel(name+'Lab')
                    field.optValue = self.app.getEntry(name)
                exp.UpdateUI(self.app)
                break

    def hideAll(self):
        for exp in self.experiments:
            for field in exp.options.itervalues():
                name = exp.name+field.optName
                if field.optType == "num":
                    self.app.hideEntry(name)
                elif field.optType == "txt":
                    self.app.hideEntry(name)
                self.app.hideLabel(name+'Lab')
                
#Starts the GUI. 
    def startGUI(self):
        self.app.go()


