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
        try:
            if name:
                for c in self.vm.get_classes():
                    if name == c.name:
                        return c
                        break
        except Exception as e:
            raise e

    def print_methods(self, c):
        """
        Print methods from a target class helper function.

        Args:
            param1: androguard.core.bytecodes.dvm.ClassDefItem

        Returns:
            None
        """
        try:
            if c:
                for m in c.get_methods():
                    if m.code:
                        print(m.pretty_show())
            else:
                return
        except Exception as e:
            raise e

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
