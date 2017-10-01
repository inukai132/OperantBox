from __future__ import print_function
import threading, time, sys

class ExperimentThread(threading.Thread):
	experiment = None
	running = False
	startTime = 0

	def __init__(self, experiment):
		self.experiment = experiment
		threading.Thread.__init__(self)

	def run(self):
		if len(self.experiment.expScript) == 0:
			raise RuntimeError("Experiment Script not loaded")
		self.startTime = time.time()
		for line in self.experiment.expScript:
			if len(line) == 1:
				line[0]()
			else:
				line[0](*line[1:])
			self.update()
			if not self.running:
				self.experiment.board.stop_board()
				#print ('Exp Thread Done')
				return
		#print ('Exp Thread Done')
		return
	
	def update(self):
	#print("Time Start: " + str(self.startTime) + ", Time Now: " + str(time.time() - self.startTime) + ", Time End:" + str(self.experiment.options["expLen"].optValue + self.startTime),end='\n')
	#sys.stdout.flush()
		if (time.time() - self.startTime) >= self.experiment.options["expLen"].optValue:
			if self.running:
				self.experiment.ExpEnd()
				self.running = False
