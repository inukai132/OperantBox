from appJar import gui
import ArduinoHandler as ard
import time

class ControllerHandler(object):
    app = gui("Control Test")
    board = None
    states = {
        ard.NosePoke:["Pin 2: Nose Poke","CheckBox"],
        ard.Reward:["Pin 3: Reward","CheckBox"],
        ard.HouseLight:["Pin 5: House Light","CheckBox"],
        ard.Servo:["Pin 6: Servo","Scale"],
        ard.CueLight:["Pin 7: Cue Light","CheckBox"],
        ard.Lever:["Pin 8: Lever","CheckBox"],
        ard.NosePokeLight:["Pin 12: Nose Poke Light","CheckBox"]
    }

    def cbUpdate(self, state, name):
        print"CB: "+str(name)+": "+str(state)+"@ "+time.strftime("%H:%M:%S")
        self.app.setCheckBox(name, state)

    def scaleUpdate(self,val):
        print("Servo Scale: "+str(val))
        self.board.set(ard.Servo, float(val))
    
    def __init__(self):
        if len(self.states) != len(ard.Pins):
            print "WARNING: This may not have all of the controls mapped"
        self.initBoard()
        self.initUI()

    def initBoard(self):
        self.board = ard.ArduinoHandler()
        self.board.start_board()

    def initUI(self):
        self.app.setFont(14)
        self.app.startLabelFrame("Signals from Box",0,0)
        for state in self.states.keys():
            if 'i' in state:
                if self.states[state][1] == "CheckBox":
                    self.app.addCheckBox(self.states[state][0])
                    self.app.getCheckBoxWidget(self.states[state][0]).config(state='disabled')
                    self.board.addCallback(self.states[state][0], self.cbUpdate, state)
        self.app.stopLabelFrame()          
        self.app.startLabelFrame("Signals to Box",0,1)
        for state in self.states.keys():
            if not 'i' in state:
                if self.states[state][1] == "CheckBox":
                    self.app.addCheckBox(self.states[state][0])
                    self.app.getCheckBoxWidget(self.states[state][0]).bind("<ButtonRelease-1>",self.update)
                elif self.states[state][1] == "Scale":
                    self.app.addLabel(self.states[state][0]+" label",self.states[state][0])
                    self.app.addScale(self.states[state][0],0,255)
                    self.app.getScaleWidget(self.states[state][0]).config(command=self.scaleUpdate)
        self.app.stopLabelFrame()
        
    def startUI(self):
        self.app.go()

    def __del__(self):
        self.board.running = False
        del self.board

    def update(self,e):
        for state in self.states.keys():
            if not 'i' in state:
                s = None
                if self.states[state][1] == "CheckBox":
                    s = self.app.getCheckBox(self.states[state][0])
                    self.board.set(state,s)
                print self.states[state][1]+": "+self.states[state][0]+" is "+str(s)


if __name__ == "__main__":        
    c = ControllerHandler()
    c.startUI()
    c.__del__()
    print 'done'
    
