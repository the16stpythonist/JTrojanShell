__author__ = 'Jonas'
from JTShell.shell import Shell
from JTShell.util.message import Message
from JTShell.util.ansi import Colors
from serverconnection import FlowControlClient
import JTShell.util.error as error
import sys
import time


class TrojanShell(Shell):

    def __init__(self, commandfolder, supershell=None):
        # initializing the parent class
        super(TrojanShell, self).__init__(commandfolder, supershell)
        # the default port on which the trojans operate usually
        if supershell is None:
            # updating the shell command prompt
            self.prompt = "\n TrojanControl> "
            # assigning the client to communicate with the FlowControlServer
            self.client = FlowControlClient()
            self.client.start()
        elif isinstance(supershell, TrojanShell):
            self.client = supershell.client

    def run(self):
        """
        the main method of the shell running the infinite loop, continuesly prompting for a command, then attempting to
        execute the issued command
        :return: (void)
        """
        time.sleep(0.5)
        # checking fot the Server status, on default everything should work though
        if self.client.ping() is True:
            self.client.update()
            # printing the initial information about the connected trojans
            print(self.client.get_info_available())

        # opening the infinite loop inside of a try statement, so that the SystemExit Exception can be caught
        try:
            while True:
                # first fetching the user input
                print(self.prompt[:-2] + Colors.MAGENTA + self.prompt[-2:] + Colors.WHITE, end="")
                command = input()

                if command == "exit":
                    if self.supershell is None:
                        sys.exit()
                    else:
                        break
                # skipping the whole procedure in case the command prompt is empty
                if command != "" and command != " ":
                    # then converting the command into a token list via the parse method
                    tokenlist = self.parser.parse(command)
                    # checking for any potential errors
                    try:
                        self.analyzer.analyze(tokenlist, command)
                        # in case the analyzer didnt raise any errors attempting to execute the tokenlist
                        last_process = self.executer.execute(tokenlist)
                        while not(last_process.status == "terminated"):
                            pass
                        if last_process.is_foreground():
                            if last_process.output is not None and not last_process.output == "":
                                if last_process.exit_status is True:
                                    print(Message("result", last_process.output).message)
                                elif last_process.exit_status is False:
                                    print(last_process.output)
                    except error.SyntaxError as e:
                        print(e.message.message)
        except SystemExit:
            pass