__author__ = 'Jonas'
import threading
import socket


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
        if self.connected is True:
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
