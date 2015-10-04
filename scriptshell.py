__author__ = 'Jonas'
from trojanshell import TrojanShell
import sys


class ScriptShell(TrojanShell):

    def __init__(self, commandfolder, supershell):
        super(ScriptShell, self).__init__(commandfolder, supershell)
        if isinstance(supershell, TrojanShell):
            self.prompt = supershell.prompt[:-2] + "|script> "
