__author__ = 'Jonas'
from trojanshell import TrojanShell
import JTShell.lib.colorama as colorama


if __name__ == '__main__':
    # initializing the colorama module, so that the ansi escape sequence colors can actually be utilized in the shell
    colorama.init()
    TrojanShell("cmds").run()