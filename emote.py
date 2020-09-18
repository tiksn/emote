import sys
from collections import OrderedDict

from knack import CLI, ArgumentsContext, CLICommandsLoader
from knack.commands import CommandGroup


def repository_update(URL):
    return f'{URL} not implemented'

class MyCommandsLoader(CLICommandsLoader):
    def load_command_table(self, args):
        with CommandGroup(self, 'repository', '__main__#{}') as g:
            g.command('update', 'repository_update')
        return OrderedDict(self.command_table)

    def load_arguments(self, command):
        with ArgumentsContext(self, 'repository update') as ac:
            ac.argument('URL', type=str)
        super(MyCommandsLoader, self).load_arguments(command)


emote = CLI(cli_name='emote', commands_loader_cls=MyCommandsLoader)
exit_code = emote.invoke(sys.argv[1:])
sys.exit(exit_code)
