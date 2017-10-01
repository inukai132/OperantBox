import random

import datetime

from ExperimentBase import Experiment
from ExperimentBase import expOption

class NosePokeTrain(Experiment):
	options = {
		"expLen":expOption("Length of Experiment (s)","num", True, 3600.0),
		"triLen":expOption("Trial Time (s)","num", False, 40),
		"triNum":expOption("Number of Trials","num", True, 3600/40),
		"cueLen":expOption("Cue Time (s)","num", True, 10),
		"reward":expOption("Reward Size (mL)","num", True, 0.5),
		"levReq":expOption("Required Lever Presses","num", True, 30)
	}
	name = "Nose Poke Shaping"
	leverPresses = 0
	nosePokes = 0
	nosePokeWaiting = False
	trialEnd = True
	currentTime = 0

	def NosePoke(self, state, name):
		self.LogOutput("Nosepoke," + self.encodeState(state) + ',')
		if not self.trialEnd: #If the trial is not over
			if not self.nosePokeWaiting and state: #If the nosepoke has not happened yet
				self.NosePokeLight(False)
				self.nosePokeWaiting = True
				self.nosePokes += 1
				self.LogOutput("Successful Nose Pokes,"+str(self.nosePokes)+",")
				self.LeverLight(True)
				self.LeverExtend()

	def Lever(self, state, name):
		self.LogOutput("Lever,"+self.encodeState(state)+',')
		if not self.trialEnd:
			if self.nosePokeWaiting and state:
				self.nosePokeWaiting = False
				self.trialEnd = True
				self.LeverLight(False)
				self.LeverRetract()
				self.leverPresses += 1
				self.LogOutput("Successful Lever Presses,"+str(self.leverPresses)+",")
				self.NosePokeLight(True)
				self.HouseLight(False)
				self.Reward(self.options["reward"].optValue*self.mLtoS)

	def Report(self):
		self.LogOutput("End,Lever Presses,"+str(self.leverPresses))
		self.LogOutput("End,Required Presses,"+str(self.options["levReq"].optValue))
		if self.leverPresses >= self.options["levReq"].optValue:
			self.LogOutput("End,Requirements Met,")
		else:
			self.LogOutput("End,Requirements Not Met,")


	def startTrialLoop(self):
		self.HouseLight(False)
		self.NosePokeLight(False)
		self.LeverLight(False)
		self.LeverRetract()
		self.nosePokeWaiting = False

	def endTrialLoop(self):
		self.trialEnd = True
		self.HouseLight(False)
		self.NosePokeLight(False)
		self.LeverLight(False)
		self.LeverRetract()
		self.nosePokeWaiting = False

	def mouseCue(self):
		self.HouseLight(True)
		self.NosePokeLight(True)
		self.trialEnd = False

	def UpdateUI(self, UI):
		startEn = True
		for field in self.options.itervalues():
			startEn = startEn and (len(str(UI.getEntry(self.name + field.optName))) > 0)

		expLen = float(UI.getEntry(self.name + self.options["expLen"].optName))
		numTri = float(UI.getEntry(self.name + self.options["triNum"].optName))
		reward = float(UI.getEntry(self.name + self.options["reward"].optName) * self.mLtoS)
		if numTri == 0:
			triLen = 0
			startEn = False
		else:
			triLen = expLen / numTri - reward
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

	def Load(self):
		self.expScript = []
		self.expScript.append([self.ExpStart])
		self.expScript.append([self.StartNosePoke])
		self.expScript.append([self.StartLever])
		random.seed()
		for i in range(1,int(self.options["triNum"].optValue)):
			waitTime = random.uniform(0,self.options["triLen"].optValue/2.0)
			self.expScript.append([self.startTrialLoop])
			self.expScript.append([self.Wait, waitTime])
			self.expScript.append([self.mouseCue])
			self.expScript.append([self.Wait, self.options["triLen"].optValue-waitTime])
			self.expScript.append([self.endTrialLoop])
		self.expScript.append([self.StopNosePoke])
		self.expScript.append([self.StopLever])
		self.expScript.append([self.LeverRetract])
		self.expScript.append([self.HouseLight,False])
		self.expScript.append([self.ExpEnd])

nosePokeTrain = NosePokeTrain()
