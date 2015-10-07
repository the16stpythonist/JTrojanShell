__author__ = 'Jonas'


def run(process):
    shell = process.shell
    shell.client.update()
    return shell.client.get_info_available()