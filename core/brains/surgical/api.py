from core.logging.logger import Logger
from . modules.web import WebModule
from . modules.intent import IntentModule
from blessings import Terminal
from datetime import datetime


class Surgical(object):

    def __init__(self, vm, vmx, package):
        self.logger = Logger()
        self.t = Terminal()
        self.vm = vm
        self.vmx = vmx
        self.package = package
        self.logger.log("info", "Loading modules ...\n")
        self.web = WebModule(self.vm, self.vmx, self.package)
        self.intent = IntentModule(self.vm, self.vmx, self.package)
        self.modules = [m for m in self.web, self.intent]


    def run(self):
        """
        Surgical's main API handler

        Args:
            None

        Returns:
            None
        """
        for m in self.modules:
            print(self.t.cyan("\t--> {}".format(m.name)))
        print("\n")
        while True:
            self.logger.log("info", "Enter 'quit' or 'exit' to leave the surgical module")
            target = raw_input(self.t.green("[{}] ".format(datetime.now())) + self.t.yellow("Select Module : "))
            if target == "quit" or target == "exit":
                # Break the loop and return to the main lobotomy menu
                break
            elif target == "list":
                # Print the loaded modules
                print("\n")
                for m in self.modules:
                    print(self.t.cyan("\t--> {}".format(m.name)))
                print("\n")
            else:
                for m in self.modules:
                    if target == m.name:
                        m.run()
