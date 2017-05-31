import random
import time
import ArduinoHandler as ard

'''
Experiment is the base class for different experiment scripts
Experiment defines all of the methods used in experiments
Classes that inherit from this should populate expScript in an overridden Load function
'''
class Experiment(object):
    
    expTime = numTrial = trialTime = rewardSize = ""
    expScript = []
    buffer = 7
    outData = []
    trialNum = 1
    expGo = True
    board = None

    timeStart = 0
    sf = 1.0
    servoIn = 0
    servoOut = 50

#Starts the experiment. Marks the starting time and starts the board
    def ExpStart(self):
        self.timeStart = time.time()
        self.LogOutput("DEBUG,Speed Factor,"+str(self.sf))
        self.LogOutput("Start,,")
        self.board.start_board()
        
#Ends the experiment and closes the board
    def ExpEnd(self):
        self.LogOutput("End,,")
        self.board.stop_board()
        self.expGo = False
        self.handler.StopExperiment()

#Sets the houselight
    def HouseLight(self,state):
        self.LogOutput("House Light,Entry,"+str(state))
        self.board.set(ard.HouseLight, state)

#Starts the nosepoke callback
    def StartNosePoke(self):
        self.LogOutput("Starting Nosepoke Sensor,,")
        self.board.addCallback("NosePoke", self.NosePoke, ard.NosePoke)

#Ends the nosepoke callback   
    def StopNosePoke(self):
        self.LogOutput("Stopping Nosepoke Sensor,,")
        self.board.removeCallback("NosePoke")

#Starts the lever callback
    def StartLever(self):
        self.LogOutput("Starting Lever Sensor,,")
        self.board.addCallback("Lever", self.Lever, ard.Lever)

#Converts true/false to entry/exit
    def encodeState(self, state):
        if state:
            return 'Entry'
        return 'Exit'
    
#Ends the lever callback
    def StopLever(self):
        self.LogOutput("Stopping Lever Sensor,,")
        self.board.removeCallback("Lever")

#Lever callback, outputs the state of the lever
    def Lever(self,state,name):
        self.LogOutput("Lever,"+self.encodeState(not state)+',')

#Nosepoke callback, outputs teh state of the sensor
    def NosePoke(self,state,name):
        self.LogOutput("Nosepoke,"+self.encodeState(not state)+',')

#Sets the nosepoke light
    def NosePokeLight(self,state):
        self.LogOutput("Nosepoke Light,Entry,"+str(state))
        self.board.set(ard.NosePokeLight, state)

#Sets the servo position
    def Servo(self,perc):
        self.LogOutput("Servo,Entry,"+str(perc))
        self.board.set(ard.Servo, perc)

#Marks the beginning of a trial
    def StartTrialLoop(self):
        self.LogOutput("Trial "+str(self.trialNum)+",Entry,")
        self.Buffer(self.buffer)

#Marks the end of a trial
    def StopTrialLoop(self):
        self.LogOutput("Trial "+str(self.trialNum)+",Exit,")
        self.trialNum += 1
        self.Buffer(self.buffer)

#Waits 
    def Wait(self,length):
        self.LogOutput("Wait,,"+"{0:.2f}".format(length))
        time.sleep(length/self.sf)
        
#Buffer, this is a predefined time between trials  
    def Buffer(self,length):
        self.LogOutput("Buffer,,"+"{0:.2f}".format(length))
        time.sleep(length/self.sf)

#Rewards the subject
    def Reward(self,amount):
        self.LogOutput("Reward,Entry,")
        self.board.pulse(ard.Reward, amount)
        self.LogOutput("Reward,Exit,")

#Aborts the test back to its original state
    def Abort(self):
        self.HouseLight(False)
        self.NosePokeLight(False)
        self.StopNosePoke()
        self.StopTrialLoop()
        self.ExpEnd()
        
#Constructor for the test
    def __init__(self, expTime, numTrial, trialTime, rewardSize, sf, buffer, handler):
        self.expTime = expTime
        self.numTrial = numTrial
        self.trialTime = trialTime
        self.rewardSize = rewardSize
        self.outData = []
        self.handler = handler
        self.sf = sf
        self.buffer = buffer / 2.0

#Potential to load experiments from a file
    def Load(self,path):
        print("Loading from "+path)

#Log output data to include the timestamp
    def LogOutput(self, data):
        out = '\t'.join(["{0:.2f}".format(time.time()-self.timeStart)]+data.split(','))
        self.outData.append(out)
        self.handler.WriteToTextBox(out)

#Appends a line to the scrolling window
    def addLine(self, fn, *args):
        line = [fn]
        for arg in args:
            line.append(arg)
        self.expScript.append(line)

#Quits the board
    def quitBoard(self):
        if self.board != None:
            #print 'quitting board'
            self.board.closeCom()
'''
Magazine Training Experiment
Will randomly reward the subject while recording nosepokes
'''

class MagTrainExperiment(Experiment):
    def Load(self, path=""):
        random.seed()
        self.expScript = []
        self.addLine(self.ExpStart)
        self.addLine(self.HouseLight,True)
        self.expScript.append([self.NosePokeLight,True])
        self.expScript.append([self.StartNosePoke])
        for i in range(self.numTrial):
            self.expScript.append([self.StartTrialLoop])
            waitTime = random.uniform(self.rewardSize/2.0,self.trialTime-self.rewardSize/2.0)
            self.expScript.append([self.Wait,waitTime-self.rewardSize/2.0])
            self.expScript.append([self.Reward,self.rewardSize])
            self.expScript.append([self.Wait,self.trialTime - waitTime-self.rewardSize/2.0])
            self.expScript.append([self.StopTrialLoop])
        self.expScript.append([self.NosePokeLight,False])
        self.expScript.append([self.HouseLight,False])
        self.expScript.append([self.StopNosePoke])
        self.expScript.append([self.ExpEnd])
            
            
            
class TestExperiment(Experiment):
    def Load(self, path=""):
        self.expScript = []
        self.expScript.append([self.ExpStart])
        self.expScript.append([self.StartNosePoke])
        self.expScript.append([self.HouseLight,True])
        self.expScript.append([self.Wait, 100])
        self.expScript.append([self.HouseLight,False])
        self.expScript.append([self.StopNosePoke])
        self.expScript.append([self.ExpEnd])
            
