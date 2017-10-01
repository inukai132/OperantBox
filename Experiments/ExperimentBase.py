import time
import ArduinoHandler as ard
from appJar import gui
import ExperimentThread

class Experiment(object):
	options = []
	mLtoS = 2.36
	board = None
	outData = []
	outTxt = []
	servoIn = 0
	servoOut = 100
	timeStart = 0
	expThread = None
	trialNum = 0
	expScript = []
	app = None
	name = ""

	def StartUI(self, board):
		self.board = board
		self.makeUI()
		self.app.go()

	def makeUI(self):
		self.app = gui(self.name)
		self.app.setGeometry(400, 900)
		self.app.addScrolledTextArea("Output")
		self.app.setTextAreaHeight("Output", 38)
		self.app.startLabelFrame("Control", 3, 0)
		self.app.addButton("Start", self.StartExperiment, 0, 0)
		self.app.addButton("Stop", self.StopExperiment, 0, 1)
		self.app.addButton("Export", self.WriteFile, 0, 2)
		self.app.disableButton("Stop")
		self.app.disableButton("Export")
		self.app.stopLabelFrame()
		self.app.setPollTime(1)
		self.app.registerEvent(self.update)
		self.app.setStopFunction(self.Close)

	def StartExperiment(self, name=""):
		self.outTxt = "Start " + str(self.name) + ":\nParameters:"
		for op in self.options.itervalues():
			self.outTxt += '\n' + op.optName + ": " + str(op.optValue)
		self.expThread = ExperimentThread.ExperimentThread(self)
		self.app.disableButton("Start")
		self.app.disableButton("Export")
		self.app.enableButton("Stop")
		self.expThread.running = True
		self.expThread.setDaemon(True)
		self.expThread.start()

	def StopExperiment(self, name=""):
		self.app.enableButton("Start")
		self.app.disableButton("Stop")
		self.app.enableButton("Export")
		self.expThread.running = False

	def WriteFile(self, name=""):
		f = self.app.saveBox(title="Export Data...", fileName=self.name+" - "+str(time.strftime("%d%b%Y")), fileExt=".csv", asFile=True)
		f.write(self.outTxt.replace('\t',','))
		f.close()
		self.app.infoBox("Export Complete", "File exported to: "+f.name)


	def Report(self):
		raise NotImplementedError

	def UpdateUI(self, UI):
		return

	# Starts the experiment. Marks the starting time and starts the board
	def ExpStart(self):
		self.timeStart = time.time()
		self.LogOutput("Start,,")
		self.board.start_board()

	# Ends the experiment and closes the board
	def ExpEnd(self):
		self.Report()
		self.board.stop_board()
		self.StopExperiment()

	# Sets the houselight
	def HouseLight(self, state):
		self.LogOutput("House Light,Entry," + str(state))
		self.board.set(ard.HouseLight, state)

	# Starts the nosepoke callback
	def StartNosePoke(self):
		self.LogOutput("Starting Nosepoke Sensor,,")
		self.board.addCallback("NosePoke", self.NosePoke, ard.NosePoke)

	# Ends the nosepoke callback
	def StopNosePoke(self):
		self.LogOutput("Stopping Nosepoke Sensor,,")
		self.board.removeCallback("NosePoke")

	# Starts the lever callback
	def StartLever(self):
		self.LogOutput("Starting Lever Sensor,,")
		self.board.addCallback("Lever", self.Lever, ard.Lever)

	# Converts true/false to entry/exit
	def encodeState(self, state):
		if state:
			return 'Entry'
		return 'Exit'

	# Ends the lever callback
	def StopLever(self):
		self.LogOutput("Stopping Lever Sensor,,")
		self.board.removeCallback("Lever")

	# Lever callback, outputs the state of the lever
	def Lever(self, state, name):
		self.LogOutput("Lever," + self.encodeState(not state) + ',')

	# Nosepoke callback, outputs the state of the sensor
	def NosePoke(self, state, name):
		self.LogOutput("Nosepoke," + self.encodeState(state) + ',')

	# Sets the nosepoke light
	def NosePokeLight(self, state):
		self.LogOutput("Nosepoke Light,Entry," + str(state))
		self.board.set(ard.NosePokeLight, state)

	# Sets the servo position
	def Servo(self, perc):
		self.LogOutput("Servo,Entry," + str(perc))
		self.board.set(ard.Servo, perc)

	def LeverLight(self, state):
		self.LogOutput("Lever Cue Light,Entry,"+str(state))
		self.board.set(ard.CueLight, state)

	# Extend the lever
	def LeverExtend(self):
		self.Servo(self.servoOut)

	# Retract the lever
	def LeverRetract(self):
		self.Servo(self.servoIn)

	# Marks the beginning of a trial
	def StartTrialLoop(self):
		self.LogOutput("Trial " + str(self.trialNum) + ",Entry,")

	# Marks the end of a trial
	def StopTrialLoop(self):
		self.LogOutput("Trial " + str(self.trialNum) + ",Exit,")
		self.trialNum += 1

	# Waits
	def Wait(self, length):
		self.LogOutput("Wait,," + "{0:.2f}".format(length))
		time.sleep(length)

	# Buffer, this is a predefined time between trials
	def Buffer(self, length):
		self.LogOutput("Wait,," + "{0:.2f}".format(length))
		time.sleep(length)

	# Rewards the subject
	def Reward(self, amount):
		self.LogOutput("Reward,Entry,")
		self.board.pulse(ard.Reward, amount)
		self.LogOutput("Reward,Exit,")

	# Aborts the test back to its original state
	def Abort(self):
		self.HouseLight(False)
		self.NosePokeLight(False)
		self.StopNosePoke()
		self.StopTrialLoop()
		self.ExpEnd()

	# Potential to load experiments from a file
	def Load(self, path):
		print("Loading from " + path)

	# Log output data to include the timestamp
	def LogOutput(self, data):
		out = '\t'.join(["{0:.2f}".format(time.time() - self.timeStart)] + data.split(','))
		self.outData.append(out)
		self.WriteToTextBox(out)

	# Quits the board
	def quitBoard(self):
		if self.board is not None:
			self.board.closeCom()

	def StopExperiment(self, name=""):
		self.expThread.running = False

	# Sends a message to the textbox
	def WriteToTextBox(self, message):
		self.outTxt += '\n' + message

	# Updates the textbox to show the new messages
	def update(self):
		txt = self.app.getTextArea("Output")
		if txt != self.outTxt:
			self.app.clearTextArea("Output")
			self.app.setTextArea("Output", self.outTxt)
			self.app.getTextAreaWidget("Output").yview_moveto(1.0)

	def Close(self):
		if self.expThread is not None:
			if self.expThread.running:
				self.expThread.running = False
		self.quitBoard()
		return True

class expOption(object):
	def __init__(self, optName, optType, optEnabled, optDefault):
		self.optName = optName
		self.optType = optType
		self.optEnabled = optEnabled
		self.optValue = optDefault

