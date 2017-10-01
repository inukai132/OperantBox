from appJar import gui
import ArduinoHandler as ard
from Camera import CameraController as Camera
import time, platform

'''
This defines the control window.
This window is used to test all features of the Arduino and the Camera
'''


class ControllerHandler(object):
	app = gui("Control Test")
	board = camera = None
	states = {
		ard.NosePoke: ["Pin 2: Nose Poke", "CheckBox"],
		ard.Reward: ["Pin 3: Reward", "CheckBox"],
		ard.HouseLight: ["Pin 5: House Light", "CheckBox"],
		ard.Servo: ["Pin 6: Servo", "Scale"],
		ard.CueLight: ["Pin 7: Cue Light", "CheckBox"],
		ard.Lever: ["Pin 8: Lever", "CheckBox"],
		ard.NosePokeLight: ["Pin 12: Nose Poke Light", "CheckBox"]
	}

	# This is a callback. This function is ran whenever an input pin changes
	def cbUpdate(self, state, name):
		# print"CB: "+str(name)+": "+str(state)+"@ "+time.strftime("%H:%M:%S")
		self.app.setCheckBox(name, state)

	# Prints and sets the current servo position
	def scaleUpdate(self, val):
		print("Servo Scale: " + str(val))
		self.board.set(ard.Servo, float(val))

	# Constructor, used to initialize the UI
	def __init__(self):
		if len(self.states) != len(ard.Pins):
			print "WARNING: This may not have all of the controls mapped"
		if platform.system() != 'Windows':
			self.camera = Camera()
			self.camera.start()

		# Creates the UI object

	def initUI(self):
		self.app = gui("Control Test")
		self.app.setFont(14)
		self.app.startLabelFrame("Signals from Box", 0, 0)
		for state in self.states.keys():
			if 'i' in state:
				if self.states[state][1] == "CheckBox":
					self.app.addCheckBox(self.states[state][0])
					self.app.getCheckBoxWidget(self.states[state][0]).config(state='disabled')
					self.board.addCallback(self.states[state][0], self.cbUpdate, state)
		self.app.stopLabelFrame()
		self.app.startLabelFrame("Signals to Box", 0, 1)
		for state in self.states.keys():
			if not 'i' in state:
				if self.states[state][1] == "CheckBox":
					self.app.addCheckBox(self.states[state][0])
					self.app.getCheckBoxWidget(self.states[state][0]).bind("<ButtonRelease-1>", self.update)
				elif self.states[state][1] == "Scale":
					self.app.addLabel(self.states[state][0] + " label", self.states[state][0])
					self.app.addScale(self.states[state][0], 0, 255)
					self.app.getScaleWidget(self.states[state][0]).config(command=self.scaleUpdate)
		self.app.stopLabelFrame()
		if platform.system() != 'Windows':
			self.app.addButton("Open Camera", self.openBrowser, 1, 0)
			self.app.addButton("Start Recording", self.startRecording, 1, 1)
			self.app.getButtonWidget("Start Recording").config(command=self.startRecording)
		self.app.setStopFunction(self.Close)

	def openBrowser(self, name):
		self.camera.openBrowser()

	def startRecording(self):
		self.camera.startRecord()
		self.app.getButtonWidget("Start Recording").config(text="Stop Recording", command=self.stopRecording)

	def stopRecording(self):
		self.camera.stopRecord()
		self.app.getButtonWidget("Start Recording").config(text="Start Recording", command=self.startRecording)

	def Load(self):
		return

	# Starts the UI
	def StartUI(self, board):
		self.board = board
		self.initUI()
		self.board.start_board()
		self.app.go()

	# When the window is closed the handler will try to close the board cleanly
	def Close(self):
		if platform.system() != 'Windows':
			self.camera.stop()
		self.board.closeCom()
		return True

	# Updates the checkboxes if the callback has happened, or calls the proper function
	def update(self, e):
		for state in self.states.keys():
			if not 'i' in state:
				s = None
				if self.states[state][1] == "CheckBox":
					s = self.app.getCheckBox(self.states[state][0])
					if e.widget.DEFAULT_TEXT == self.states[state][0]:
						s = not s
					self.board.set(state, s)
				print self.states[state][1] + ": " + self.states[state][0] + " is " + str(s)


if __name__ == "__main__":
	c = ControllerHandler()
	c.StartUI()
	print 'done'
