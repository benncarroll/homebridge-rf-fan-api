from os import system
from subprocess import run, PIPE
from sys import platform
import logging
from time import sleep


def establishConnection():
    if platform == 'darwin':
        return True
    stat = system("sudo service pilight status >/dev/null 2>&1")
    if stat:
        sleep(2)
        establishConnection()
    return True


def sendCode(signal):
    establishConnection()
    if signal != '':
        logging.getLogger('api').debug(signal)
        if platform == 'darwin':
            return
        system("pilight-send -p raw -c '%s'" % signal)
