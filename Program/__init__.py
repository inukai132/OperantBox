#!/usr/bin/python2
from appUI import GUI
import time
from ArduinoHandler import ArduinoHandler as AH

TestHandler = None
Board = None
exitCode = 0
while exitCode == 0:
    with GUI() as UI:
        UI.startGUI()
        if UI.exitCode == 0:
            TestHandler = UI.handler
        else:
            break
        
    if TestHandler != None:
        if Board == None:
            Board = AH()
            #exitCode = -1
        TestHandler.startUI(Board)
print 'done'
#test
