import random
import time
import ArduinoHandler as ard

sf = 10.0

class Experiment(object):
    
    expTime = numTrial = trialTime = rewardSize = ""
    expScript = []
    buffer = 7
    outData = []
    trialNum = 1
    expGo = True
    board = None
    timeStart = 0
    
    
    def ExpStart(self):
        self.LogOutput("Experiment Start")
        self.LogOutput("DEBUG: Speed Factor "+str(sf))
        self.board.start_board()
        
    def ExpEnd(self):
        self.LogOutput("Experiment End")
        self.board.stop_board()
    
    def HouseLight(self,state):
        self.LogOutput("House Light: "+str(state))
        self.board.set(ard.HouseLight, state)
    
    def StartNosePoke(self):
        self.LogOutput("Starting Nose Poke Sensor")
        self.board.addCallback("NosePoke", self.NosePoke, ard.NosePoke)
    
    def StopNosePoke(self):
        self.LogOutput("Stopping Nose Poke Sensor")
        self.board.removeCallback("NosePoke")
    
    def NosePoke(self,state):
        self.LogOutput("Nose Poke Sensor: "+str(not state))
    
    def NosePokeLight(self,state):
        self.LogOutput("Nose Poke Light: "+str(state))
        self.board.set(ard.NosePokeLight, state)
        
    def StartTrialLoop(self):
        self.LogOutput("Trial "+self.trialNum+" Begin")
        
    def StopTrialLoop(self):
        self.LogOutput("Trial "+self.trialNum+" End")
        self.trialNum += 1
        
    def Wait(self,length):
        self.LogOutput("Waiting for "+str(length)+" sec")
        time.sleep(length/sf)
        
    def Reward(self,amount):
        self.LogOutput("Rewarding "+str(amount)+"mL")
        self.board.pulse(ard.Reward, self.rewardSize)
    
    def SetExp(self, val):
        self.expGo = val
        
    def Abort(self):
        self.HouseLight(False)
        self.NosePokeLight(False)
        self.StopNosePoke()
        self.StopTrialLoop()
        self.ExpEnd()
        

    def __init__(self, expTime, numTrial, trialTime, rewardSize, handler):
        self.expTime = expTime
        self.numTrial = numTrial
        self.trialTime = trialTime-self.buffer*2
        self.rewardSize = rewardSize
        self.outData = []
        self.handler = handler
        self.board = ard.ArduinoHandler()
        
    def Load(self,path):
        print("Loading from "+path)
        
    def RunExperiment(self):
        if len(self.expScript) == 0:
            raise RuntimeError("Experiment Script not loaded")
        self.timeStart = time.time()
        for line in self.expScript:
            if len(line) == 1:
                line[0]()
            else:
                line[0](*line[1:])
            if self.expGo == False:
                return
        self.handler.StopExperiment()
        
    def LogOutput(self, data):
        out = "{0:.2f}".format(time.time()-self.timeStart) + ":\t" + data
        self.outData.append(out)
        self.handler.WriteToTextBox(out)
        
            
        
class MagTrainExperiment(Experiment):
    def Load(self, path=""):
        random.seed()
        self.expScript = []
        self.expScript.append([self.ExpStart])
        self.expScript.append([self.HouseLight,True])
        self.expScript.append([self.NosePokeLight,True])
        self.expScript.append([self.StartNosePoke])
        for i in range(self.numTrial):
            self.expScript.append([self.StartTrialLoop])
            waitTime = random.randint(0,self.trialTime)
            self.expScript.append([self.Wait,self.buffer])
            self.expScript.append([self.Wait,waitTime])
            self.expScript.append([self.Reward,self.rewardSize])
            self.expScript.append([self.Wait,self.trialTime - waitTime])
            self.expScript.append([self.Wait,self.buffer])
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
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            