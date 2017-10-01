from ExperimentBase import Experiment, expOption

class LeverTrain(Experiment):
    options = {
        "expLen":expOption("Length of Experiment (s)", "num", True, 1800.0),
        "reqPress":expOption("Required Lever Presses", "num", True, 50),
        "reward":expOption("Reward Size (mL)", "num", True, 0.5),
    }
    name = "Lever Press Shaping"
    leverPresses = 0
    leverWaiting = False
    currentTime = 0

    def NosePoke(self, state, name):
        self.LogOutput("Nosepoke," + self.encodeState(state) + ',')
        if self.leverWaiting and state:
            self.NosePokeLight(False)
            self.leverWaiting = False
            self.leverPresses += 1
            self.LogOutput("Successful Lever Presses,"+str(self.leverPresses)+",")

    def Lever(self, state, name):
        self.LogOutput("Lever,"+self.encodeState(state)+',')
        if not self.leverWaiting and state:
            self.Reward(self.options["reward"].optValue*self.mLtoS)
            self.NosePokeLight(True)
            self.leverWaiting = True

    def Report(self):
        self.LogOutput("End,Lever Presses,"+str(self.leverPresses))
        self.LogOutput("End,Required Presses,"+str(self.options["reqPress"].optValue))
        if self.leverPresses >= self.options["reqPress"].optValue:
            self.LogOutput("End,Requirements Met,")
        else:
            self.LogOutput("End,Requirements Not Met,")
  
    def Load(self):
        self.expScript = []
        self.expScript.append([self.ExpStart])
        self.expScript.append([self.HouseLight,True])
        self.expScript.append([self.StartNosePoke])
        self.expScript.append([self.StartLever])
        self.expScript.append([self.LeverExtend])
        self.expScript.append([self.Wait, self.options["expLen"].optValue])
        self.expScript.append([self.StopNosePoke])
        self.expScript.append([self.StopLever])
        self.expScript.append([self.LeverRetract])
        self.expScript.append([self.HouseLight,False])
        self.expScript.append([self.ExpEnd])

leverTrain = LeverTrain()
