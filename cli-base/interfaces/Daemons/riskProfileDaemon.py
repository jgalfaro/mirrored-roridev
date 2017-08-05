#!/usr/bin/python
__author__ = 'ender_al'

import time, sys
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import subprocess as sub
import os

def getRealPath():
    #Get Real System Path where this script relies
    dir_path = os.path.realpath(__file__).split('/')
    dir_path.pop()
    dir_path = "/".join(dir_path)
    return dir_path+'/'

class WatchdogHandler(PatternMatchingEventHandler):
    #Only look for any changes in JSON or txt files
    patterns = ["*.json","*.txt"]

    def process(self, event):
        print 'Processing the new file with Risk Profile Parser'
        parser_path = getRealPath().replace('Daemons/','JSONParsers/riskProfile/riskProfileParser.py')
        return_code = sub.call(['python', parser_path, '-i', event.src_path])
        if return_code != 0:
            print 'Error running the Risk Profile Parser'
            return

    def on_modified(self, event):
        print "There was a change in the Folder containing the Risk Profiles"
        self.process(event)

    def on_created(self, event):
        print "A new file was added to the Folder containing the Risk Profiles"
        #self.process(event)

if __name__ == '__main__':
    #args = sys.argv[1:]
    path = '/tmp/PANOPTESEC_InputData/RiskProfile'
    try:
        observer = Observer()
        observer.schedule(WatchdogHandler(), path)
        observer.start()
    except OSError:
        print 'Error: The path:',path,',does not exist in the system!!!'
        exit(1)

    print 'Starting the "Risk Profile Watchdog" on folder:', path
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()