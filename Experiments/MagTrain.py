import random
import time
from ExperimentBase import Experiment, expOption
import ArduinoHandler as ard

class MagTraining(Experiment):
	options = {
		"expLen":expOption("Length of Experiment (s)", "num", True, 1800.0),
		"triNum":expOption("Number of Trials", "num", True, 30),
		"buffer":expOption("Time Between Trials (s)", "num", True, 15.0),
		"triLen":expOption("Length of Trial (s)", "num", False, 60.0),
		"reward":expOption("Reward Size (mL)", "num", True, .5),
	}
	name = "Magazine Training"
	npState = 0
	npFails = 0
	nosePokes = 0

	# Starts the nosepoke callback
	def StartNosePoke(self):
		self.LogOutput("Starting Nosepoke Sensor,,")
		self.nosePokes = 0
		self.npState = -1
		self.npFails = 0
		self.board.addCallback("NosePoke", self.NosePoke, ard.NosePoke)

	# Marks the beginning of a trial
	def StartTrialLoop(self):
		self.LogOutput("Trial " + str(self.trialNum) + ",Entry,")
		self.Buffer(self.options["buffer"].optValue/2.0)
		self.trialNum += 1

	# Marks the end of a trial
	def StopTrialLoop(self):
		self.LogOutput("Trial " + str(self.trialNum) + ",Exit,")
		self.Buffer(self.options["buffer"].optValue/2.0)

	# Buffer, this is a predefined time between trials
	def Buffer(self, length):
		self.LogOutput("Wait,," + "{0:.2f}".format(length))
		for i in range(0,int(length*100)):
			time.sleep(.00974)
			self.expThread.update()
			if not self.expThread.running:
				break

	# Waits
	def Wait(self, length):
		self.LogOutput("Wait,," + "{0:.2f}".format(length))
		time.sleep(length)

	def UpdateUI(self, UI):
		startEn = True
		for field in self.options.itervalues():
			startEn = startEn and (len(str(UI.getEntry(self.name + field.optName))) > 0)

		expLen = float(UI.getEntry(self.name + self.options["expLen"].optName))
		numTri = float(UI.getEntry(self.name + self.options["triNum"].optName))
		expBuffer = float(UI.getEntry(self.name + self.options["buffer"].optName))
		reward = float(UI.getEntry(self.name + self.options["reward"].optName) * self.mLtoS)
		if numTri == 0:
			triLen = 0
			startEn = False
		else:
			triLen = expLen / numTri - expBuffer - reward
		if triLen <= 0:
			startEn = False

		UI.setEntry(self.name + self.options["triLen"].optName, str(triLen + reward))

		if not startEn:
			UI.disableButton("Start")
			UI.disableEnter()
		else:
			UI.enableButton("Start")
			UI.enableEnter(self.StartExperiment)
		return

	def StopExperiment(self, name=""):
		self.app.enableButton("Start")
		self.app.disableButton("Stop")
		self.app.enableButton("Export")
		self.expThread.running = False


	def Report(self):
		self.LogOutput("End,Nose Pokes,"+str(self.options["triNum"].optValue - self.npFails))
		self.LogOutput("End,Deliveries,"+str(self.options["triNum"].optValue))
		self.LogOutput("End,Failed Rewards,"+str(self.npFails))
		self.LogOutput("End,Success Rewards,"+str(self.options["triNum"].optValue - self.npFails))
		self.LogOutput("End,Reward Percentage,"+str(100 - (self.npFails*100/self.options["triNum"].optValue))+'%')

	def Reward(self, amount):
		self.NosePokeUpdate()
		self.npState = self.nosePokes
		self.LogOutput("Reward,Entry,")
		self.board.pulse(ard.Reward, amount)
		self.LogOutput("Reward,Exit,")

	#Called when start is pressed, this function starts the experiment

	def StartExperiment(self,name=""):
		self.trialNum = 0
		Experiment.StartExperiment(self)

	# Updates the number of nosepokes
	def NosePokeUpdate(self):
		if self.nosePokes == self.npState:
			self.npFails += 1
			success = self.trialNum - self.npFails
			self.LogOutput("Nosepoke Status,Fail,Passes: " + str(success) + " Fails: " + str(self.npFails))
		elif self.npState >= 0:
			success = self.trialNum - self.npFails
			self.LogOutput("Nosepoke Status,Fail,Passes: " + str(success) + " Fails: " + str(self.npFails))

	# Ends the experiment and closes the board
	def ExpEnd(self):
		self.NosePokeUpdate()
		self.Report()
		self.board.stop_board()
		self.StopExperiment()

	# Ran at start of the experiment. Marks the starting time and starts the board
	def ExpStart(self):
		Experiment.ExpStart(self)

	def Load(self):
		random.seed()
		self.expScript = []
		self.expScript.append([self.ExpStart])
		self.expScript.append([self.HouseLight,True])
		self.expScript.append([self.NosePokeLight,True])
		self.expScript.append([self.StartNosePoke])
		for i in range(int(self.options["triNum"].optValue)):
			waitTime = random.uniform(self.options["reward"].optValue/2.0,self.options["triLen"].optValue-self.options["reward"].optValue/2.0)
			self.expScript.append([self.StartTrialLoop])
			self.expScript.append([self.Wait,waitTime-self.options["reward"].optValue/2.0])
			self.expScript.append([self.Reward,self.options["reward"].optValue])
			self.expScript.append([self.Wait,self.options["triLen"].optValue - waitTime-self.options["reward"].optValue/2.0])
			self.expScript.append([self.NosePokeLight,False])
			self.expScript.append([self.StopTrialLoop])
		self.expScript.append([self.HouseLight,False])
		self.expScript.append([self.StopNosePoke])
		self.expScript.append([self.ExpEnd])


magTrain = MagTraining()
