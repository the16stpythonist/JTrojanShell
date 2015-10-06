__author__ = 'Jonas'
import socket
import threading
import time


class TCPClient(threading.Thread):
    """
    a simple tcp client application, capable of connecting to one single Server Application and establishing a stable
    one to one connection. Having to separate sockets for sending and receiving data, but it doesn't only receive data
    whenever the receive method is called, but rather always receives data into a local buffer and by calling the
    receive method the earliest received data is popped from the buffer and returned, alternatively one can call the
    receive_all method to get the whole list of the buffer at once, clearing it in the process.
    :ivar connected: (boolean) whether the server is currently connected to a client
    :ivar ip: (string) the ip of the server to be connected to
    :ivar running: pass
    :ivar receiving_socket: (socket) the server socket, which only receives data
    :ivar sending_socket: (socket) the client socket, only sending data
    :ivar receive_buffer: (list) the list containing all data received, since it ha been cleared the last time
    """
    def __init__(self, ip):
        super(TCPClient, self).__init__()
        self.ip = ip
        self.connected = False
        self.running = True
        self.active = True
        self.receive_buffer = []
        self.sending_socket = socket.socket()
        self.receiving_socket = socket.socket()

    def run(self):
        """
        the main loop of the Client, first attempting to connect to the server application at the passed ip, then
        continuesly receiving the data sent by the server socket
        :return: (void)
        """
        # connecting the client to the server with the given ip
        self.connect()
        while self.running:
            if self.active is True:
                try:
                    connection, adress = self.receiving_socket.accept()
                    raw_data = connection.recv(8192)
                    self.connected = True
                    self.receive_buffer.append(str(raw_data)[2:-1])
                except socket.error:
                    self.connected = False
            else:
                time.sleep(0.5)

    def connect(self, trials=10):
        """
        attempts to connect to the server a passed amount of times, before raising a connection error
        :param trials: (int) the amount of times to try cinnecting to the server
        :return:
        """
        count = 0
        while self.connected is False and count <= trials:
            try:
                # connecting the sending socket to the listening receiving socket of the the server application
                self.sending_socket.connect((self.ip, 8889))
                self.sending_socket.close()
                # configuring the receiving socket as a socket server version
                self.receiving_socket.bind(("0.0.0.0", 8887))
                self.receiving_socket.listen(10)
                self.connected = True
            except socket.error as e:
                print(str(e))
                self.connected = False
            finally:
                count += 1

    def send(self, string):
        """
        sends the passed string to the client via the sending socket of the server
        :param string: (string) the data that is to be send
        :return: (void)
        """
        if self.connected is True:
            # creating a new client socket to send the data passed to the method
            self.sending_socket = socket.socket()
            self.sending_socket.connect((self.ip, 8889))
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
        if self.active:
            self.receiving_socket.close()
        # stops the thread itself
        self.running = False

    def deactivate(self):
        """
        deactivates the Client, meaning closing the server socket with the purpose of releasing the occupied port to
        be used by other applications
        :return: (void)
        """
        # checking whether a deactivation is actually possible
        if self.active is True:
            self.active = False
            # closing the server socket, so others can use the port it previously used
            self.receiving_socket.close()

    def activate(self):
        """
        activates the Client, after it has been deactivated (and only in this case), so the client can be used again
        :return: (void)
        """
        # checking if the activation is actually needed
        if self.active is False:
            # creating a new server socket to listen on the port again
            self.receiving_socket = socket.socket()
            self.receiving_socket.bind(("0.0.0.0", 8887))
            self.receiving_socket.listen(10)
            # updating the status of the application to connected again
            self.active = True





