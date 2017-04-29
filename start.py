from appUI import GUI
import time

UI = GUI()
UI.startGUI()

TestHandler = None

if UI.exitCode == 0:
    TestHandler = UI.handler
    TestHandler.startUI()