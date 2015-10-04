__author__ = 'Jonas'
from JTShell.util.error import Error
from JTShell.util.message import Message
from JTShell.lib.JTLib.JTNetwork.client import TCPClient
import socket
from socket import error as socketerror
import time


class TrojanConnection(TCPClient):
    """
    An object, that is used to represent the connection to a given Trojan at the passed ip and port, encapsulating
    functions to properly connect the socket to the server of the trojan, send and receive data, combining the ip, port,
    socket of the connection in a single object
    :ivar connected: (boolean) whether the server is currently connected to a client
    :ivar ip: (string) the ip of the server to be connected to
    :ivar running: pass
    :ivar receiving_socket: (socket) the server socket, which only receives data
    :ivar sending_socket: (socket) the client socket, only sending data
    :ivar receive_buffer: (list) the list containing all data received, since it ha been cleared the last time
    :ivar name: (string) the name of the trojan, if there is one give
    """
    def __init__(self, ip, name=""):
        super(TrojanConnection, self).__init__(ip)
        # in case the trojan has a specific identifying name, that can also be passed
        self.name = name

    def ping(self):
        if self.connected is True:
            self.send("ping")
            time.sleep(0.1)
            if self.receive() == "ping":
                return True
            else:
                return False
        else:
            return False


class TrojanConnectionError(Error):
    """
    the Exception, that will be raised in case there is a Problem with connecting the socket of the main Trojan
    Connection object, working just as any other JTShell custom exception only having one important attribute, being
    the stored message, which is an already formatted string that can be printed to the shell when first converted
    into a string explicitly
    :param string: (string) the string message to be displayed
    :var message: (Message) the Message object, inheriting the string to be outputted to the console
    """
    def __init__(self, string):
        super(TrojanConnectionError, self).__init__()
        self.message = Message("error", string)
