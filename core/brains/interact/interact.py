from IPython.terminal.embed import InteractiveShellEmbed
from traitlets.config import Config


class Interact(object):
    def __init__(self, vm, vmx):
        self.vm = vm
        self.vmx = vmx
        self.config = Config()

    def run(self):
        """
        Args:
            None

        Returns:
            None
        """
        ipshell = InteractiveShellEmbed(config=self.config, banner1="Lobotomy Interactive")
        ipshell()
