from IPython.terminal.embed import InteractiveShellEmbed
from traitlets.config import Config


class Interact(object):
    def __init__(self, vm, vmx):
        self.vm = vm
        self.vmx = vmx
        self.config = Config()

    def find_class(self, name):
        """
        Find class helper function.

        Args:
            param1: name
        Returns:
            return: androguard.core.bytecodes.dvm.ClassDefItem
        """
        for c in self.vm.get_classes():
            if name == c.name:
                return c
                break

    def run(self):
        """
        Args:
            None

        Returns:
            None
        """
        ipshell = InteractiveShellEmbed(config=self.config,
                                        banner1="Lobotomy Interactive")
        ipshell()
