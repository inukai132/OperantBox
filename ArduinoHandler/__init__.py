from pyfirmata import Arduino, util
import serial.tools.list_ports as com
from time import sleep
import threading, weakref

'''
The Board Thread will handle communication with the Board and preforming callbacks
'''
class BoardThread(threading.Thread):
    running = False
    handler = None

    def __init__(self, handler):
        self.handler = handler
        threading.Thread.__init__(self)

    def run(self):
        while self.running and self.handler.board != None:
            while self.handler.board.bytes_available():
                self.handler.board.iterate()
            for pin in self.handler.callbacks.keys():
                p = self.handler.getPin(pin)
                state = not p.read()
                try:
                    if self.handler.pinStates[pin] != state and state != None:
                        self.handler.pinStates[pin] = state
                        self.handler.callbacks[pin][1](state,self.handler.callbacks[pin][0])
                except KeyError:
                    if state != None:
                        self.handler.pinStates[pin] = state
            sleep(.001)
        #print 'ArdHan Thread Done'
        return
'''
The Aruduino Handler should contain all code defining the Arduino
This includes Pin definitions and functions
This should be written in such a way that it can be exchanged with another
module if we change the board
'''

#Pin definitions, (d)igital/(a)nalog:number:(i)nput/(o)utput/(s)ervo
NosePoke = 'd:2:i'
Reward = 'd:3:p'
HouseLight = 'd:5:o'
Servo = 'd:6:s'
CueLight = 'd:7:o'
Lever = 'd:8:i'
NosePokeLight = 'd:12:o'
Pins = [
    NosePoke,
    Reward,
    HouseLight,
    Servo,
    CueLight,
    Lever,
    NosePokeLight]


'''
Base class, if we write a new board it should inherit from board handler
and board handler should be brought out into its own file
'''
class BoardHandler(object):
    board = None
    callbacks = {}
    running = False
    t = None
    
    def addCallback(self, name, cb, pin):
        self.callbacks[pin] = [name,cb]
        
    def removeCallback(self, name):
        for pin in self.callbacks.items():
            if name in pin: del pin
    
    def pulse(self, pin, length):
        return
    
    def toggle(self, pin):
        return
    
    def set(self, pin, val):
        return
    
    def openCom(self):
        return
    
    def start_board(self):
        self.t = BoardThread(self)
        self.t.running = True
        #print 'started'
        self.t.start()
        
    def stop_board(self):
        self.t.running = False
        
    def run(self):
        return
        
    def __init__(self):
        return
    
class ArduinoHandler(BoardHandler):
    port = ""
    pinStates = {Lever:True}
    pins = {}
    it = None

#Opens communication with the Arduino. Also creates the Arduino PyFermata object
    def openCom(self):
        ports = list(com.comports())
        for port in ports:
            if "Arduino" in port[1] or "Arduino" in port.manufacturer:
                self.port = port[0]
                print("Found Arduino at port "+self.port)
                break
        if self.port == "":
            raise EnvironmentError("Arduino not found")
            return
        self.board = Arduino(self.port)

#Closes communication with Arduino
    def closeCom(self):
        if self.t != None:
            self.t.running = False
        for name in self.pins.keys():
            if name.split(':')[-1] != 'i':
                #print 'switching off: '+name
                self.set(name, False)
        #print("Closing Connection with Arduino")
        self.board = None
        print("Closed Connection with Arduino")

#Caches pin and returns it
    def getPin(self, pin):
        if not pin in self.pins:
            self.pins[pin] = self.board.get_pin(pin)
        return self.pins[pin]
    
#Send a timed high pulse on one pin
    def pulse(self, pin_n, length):
        pin = self.getPin(pin_n)
        pin.write(True)
        sleep(length)
        pin.write(False)

#Toggle a pin
    def toggle(self, pin_n):
        pin = self.getPin(pin_n)
        pin.write(1-pin.read())

#Set a pin
    def set(self, pin_n, val):
        pin = self.getPin(pin_n)
        pin.write(val)

#Constructor, starts reporting on the input pins and creates a thread to read them      
    def __init__(self):
        self.openCom()
        self.getPin(NosePoke).enable_reporting()
        self.getPin(Lever).enable_reporting()
        #self.it = util.Iterator(self.board)
        #self.it.start()
        
        
    
