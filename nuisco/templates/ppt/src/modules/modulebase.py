# /*Imports omitted*/
from aplustools.logs import LogType
from . import link

def mbinit(): # Initialize link after it was loaded by main
    global log # Link is used for the main process and other files to communicate
    log = link.log # As a test to see if you know how this works, try implementing this script in main

def start():
    log("MB | Started", LogType.DEBUG)
