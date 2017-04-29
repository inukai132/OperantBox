from pyfirmata import Arduino, util
import serial.tools.list_ports as com
from time import sleep
import thread


NosePoke = 'd:2:i'
Reward = 'd:3:o'
HouseLight = 'd:5:o'
Servo = 'd:6:p'
CueLight = 'd:7:o'
Lever = 'd:8:o'
NosePokeLight = 'd:12:o'


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
        self.running = True
        self.t = thread.start_new_thread(self.run,())
        
    def stop_board(self):
        self.running = False
        
    def run(self):
        return
        
    def __init__(self):
        return
    
class ArduinoHandler(BoardHandler):
    port = ""
    pinStates = {NosePoke:False}
    pins = {}
    it = None
    
    def openCom(self):
        ports = list(com.comports())
        for port in ports:
            if "Arduino" in port[1] or "Arduino" in port.manufacturer:
                self.port = port[0]
                print("Found Arduino at port "+self.port)
                break
        if self.port == "":
            raise EnvironmentError("Arduino not found")
        self.board = Arduino(self.port)

    def closeCom(self):
        self.board.exit()
        print("Closing Connection with Arduino")
        
    def getPin(self, pin):
        if not pin in self.pins:
            self.pins[pin] = self.board.get_pin(pin)
        return self.pins[pin]
    
    def pulse(self, pin_n, length):
        pin = self.getPin(pin_n)
        pin.write(1)
        sleep(length)
        pin.write(0)
        
    def toggle(self, pin_n):
        pin = self.getPin(pin_n)
        pin.write(1-pin.read())
        
    def set(self, pin_n, val):
        pin = self.getPin(pin_n)
        pin.write(val)
                
    def __init__(self):
        self.openCom()
        self.getPin(NosePoke).enable_reporting()
        self.it = util.Iterator(self.board)
        self.it.start()
        
    def run(self):
        while self.running:
            for pin in self.callbacks.keys():
                p = self.getPin(pin)
                state = p.read()
                if self.pinStates[pin] != state and state != None:
                    self.pinStates[pin] = state
                    self.callbacks[pin][1](state)
            sleep(.1)
        
    
