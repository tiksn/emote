import sys
from collections import OrderedDict

from knack import CLI, ArgumentsContext, CLICommandsLoader
from knack.commands import CommandGroup


class MyCommandsLoader(CLICommandsLoader):
    def load_command_table(self, args):
        with CommandGroup(self, "repository", "repository#{}") as g:
            g.command("update", "update_repository")
        with CommandGroup(self, "source", "source#{}") as g:
            g.command("fetch", "fetch_source")
        with CommandGroup(self, "target", "target#{}") as g:
            g.command("populate", "populate_target")
        return OrderedDict(self.command_table)

    def load_arguments(self, command):
        with ArgumentsContext(self, "repository update") as ac:
            pass
        with ArgumentsContext(self, "source fetch") as ac:
            ac.argument("kind", type=str)
        with ArgumentsContext(self, "target populate") as ac:
            ac.argument("kind", type=str)
            ac.argument("api_key", type=str)
        super(MyCommandsLoader, self).load_arguments(command)


emote = CLI(cli_name="emote", commands_loader_cls=MyCommandsLoader)
exit_code = emote.invoke(sys.argv[1:])
sys.exit(exit_code)
