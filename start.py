#!/usr/bin/python2
from appUI import GUI
import time

TestHandler = None

with GUI() as UI:
    UI.startGUI()
    if UI.exitCode == 0:
        TestHandler = UI.handler

if TestHandler != None:
    TestHandler.startUI()

del TestHandler
