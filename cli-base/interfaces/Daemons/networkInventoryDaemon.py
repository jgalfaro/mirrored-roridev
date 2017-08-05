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
        print 'Processing the new file with Network Inventory Parser'
        parser_path = getRealPath().replace('Daemons/','JSONParsers/networkInventory/networkInventoryParser.py')
        return_code = sub.call(['python', parser_path, '-i', event.src_path])
        if return_code != 0:
            print 'Error running the Network Inventory Parser'
            return

    def on_modified(self, event):
        print "There was a change in the Folder containing the Network Inventory"
        self.process(event)

    def on_created(self, event):
        print "A new file was added to the Folder containing the Network Inventory"
        #self.process(event)

if __name__ == '__main__':
    #args = sys.argv[1:]
    path = '/var/PANOPTESEC/Jail/InputData/NetworkInventory'
    try:
        observer = Observer()
        observer.schedule(WatchdogHandler(), path)
        observer.start()
    except OSError:
        print 'Error: The path:',path,',does not exist in the system!!!'
        exit(1)

    print 'Starting the "Network Inventory Watchdog" on folder:', path

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()