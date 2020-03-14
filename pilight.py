from os import system
from subprocess import run, PIPE
from sys import exit, platform
import logging
from time import sleep
import asyncio

signal_queue = []
processing = False

async def processSignals():
    if processing:
        return
    processing = True


    processing = True

def waitForActive():
    stat = system("sudo service pilight status")
    print(stat)
    if stat:
        sleep(2)
        waitForActive()
    return

def establishConnection(count=0):
    if platform == 'darwin':
        return True
    waitForActive()
    count += 1
    output = run(
        ["pilight-send", "-p", "raw", "-c", "'100 100'"],
        stderr=PIPE, stdout=PIPE
    )
    if 'no pilight ssdp' in output.stderr.decode('utf-8'):
        system('sudo service pilight stop')
        system('sudo service pilight start')
        if count > 10:
            print('Aborting. Could not launch pilight.')
            exit()
        establishConnection(count)
    else:
        return True


def sendCode(signal):
    establishConnection()
    if signal != '':
        logging.getLogger('api').debug(signal)
        if platform == 'darwin':
            return
        system("pilight-send -p raw -c '%s'" % signal)
