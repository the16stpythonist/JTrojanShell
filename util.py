__author__ = 'Jonas'
import JTShell.util.colors as colors
from JTShell.util.message import Message
import inspect
import os

end_sequence = "<;end;>"

def shellprint(process, message):
    """
    The "print" function altered to work in the JTShell environment, only executing a print function in case the passed
    process object is in the foreground
    :param process: (Process) the process object of the process executing the function
    :param message: (Message) the message to be printed
    :return: (bool) whether it was printed or not
    """
    if process.is_foreground():
        print(str(message))
        return True
    else:
        return False
    

def trojanprint(process, message):
    string = TrojanMessage(message)
    if process.is_foreground():
        print(str(string))
    return string.type


def trojanrecv(process, trojanconnection):
    """
    a function which implements a while loop, that receives and, in case the passed process is foreground, prints the
    given received response of the trojan until the trojan has sent the end sequence. Returns the the type of the last
    message that has been received.
    :param process: (Process) the process object to determine whether the process is foreground or background
    :param trojanconnection: (TrojanConnection) the connection object with which to perform the receive function
    :return: (string) the type of the last message received, either "error", "process" or "result"
    """
    message_type = ""
    receiving = True
    while receiving:
        data = trojanconnection.receive()
        if data is not None:
            if end_sequence in data:
                receiving = False
            else:
                message_type = trojanprint(process, data)
    return message_type


def isip(string):
    """
    returns whether the passed string is to be handled as an ip or not
    :param string: (string) the string to be checked
    :return: (bool)
    """
    if string.count(".") == 3:
        return True
    else:
        return False


def path():
    """
    returns the path of the main folder JTrojanShell
    :return: (string) the absolute path of the folder
    """
    return str(os.path.realpath(os.path.dirname(inspect.getfile(inspect.currentframe()))))


class TrojanMessage(Message):

    def __init__(self, string):
        self.type = ""
        self.string = string.replace("\\r\\n", "\n")
        self.message = ""
        # creating the message string with the colors and symbols according
        if self.string[0:3] == "[!]":
            self.message = colors.red(str(self.string))
            self.type = "error"
        elif self.string[0:3] == "[*]":
            self.message = colors.white(str(self.string))
            self.type = "process"
        elif self.string[0:3] == "[+]":
            self.message = colors.green(str(self.string))
            self.type = "result"
