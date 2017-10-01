#!/usr/bin/python2
"""
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
        Board = AH()
        TestHandler.startUI(Board)
        Board = None
        TestHandler = None
print 'done'
"""
from StartMenu import GUI
from ArduinoHandler import ArduinoHandler

ui = GUI()
ui.startGUI()

if ui.exitCode == 0:
	board = ArduinoHandler()
	handler = ui.handler
	handler.Load()
	handler.StartUI(board)
