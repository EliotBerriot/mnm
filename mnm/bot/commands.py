import collections


class Command(object):
    pass


class Help(Command):
    code = 'help'


commands = collections.OrderedDict()
commands['help'] = Help()
