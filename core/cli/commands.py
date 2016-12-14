from cmd2 import Cmd as Lobotomy
from core.logging.logger import Logger
from blessings import Terminal
from core.brains.utilities.util import Util


class CommandError(Exception):
    def __init__(self, message):
        self.logger = Logger()
        self.message = message
        self.logger.log("critical", "Command : {}".format(self.message))


class Run(Lobotomy):
    def __init__(self):
        Lobotomy.__init__(self)
        self.t = Terminal()
        self.logger = Logger()
        self.util = Util()
        self.apk = None
        self.package = None
        self.vm = None
        self.vmx = None
        self.gmx = None
        self.components = None
        self.dex = None
        self.strings = None
        self.permissions = None
        self.permissions_details = None
        self.files = None
        self.attack_surface = None

    def find_dex(self):
        """
        Return True is classes.dex is found within the target APK.

        Args:
            None

        Returns:
            None
        """
        if self.files:
            for f in self.files:
                if "classes" in f:
                    return True
                    break

    def process_vm(self):
        """
        Process the application's classes.dex

        Args:
            None

        Results:
            None
        """
        # Make sure classes.dex exists
        if self.find_dex():
            self.dex = self.apk.get_dex()
            # Analyze classes.dex
            # TODO Throw in a progress bar, this can take awhile
            if self.dex:
                self.logger.log("info", "Loading classes.dex ...")
                from androguard.core.bytecodes.dvm import DalvikVMFormat
                from androguard.core.analysis.analysis import VMAnalysis
                from androguard.core.analysis.ganalysis import GVMAnalysis
                # Create a new virtual machine instance
                self.vm = DalvikVMFormat(self.dex)
                if self.vm:
                    print(self.t.yellow("\n\t--> Loaded classes.dex (!)\n"))
                    self.logger.log("info", "Analyzing classes.dex ...")
                    # Analyze the virtual machine instance
                    self.vmx = VMAnalysis(self.vm)
                    self.gmx = GVMAnalysis(self.vmx, None)
                    if self.vmx and self.gmx:
                        print(self.t.yellow("\n\t--> Analyzed classes.dex (!)\n"))
                        self.vm.set_vmanalysis(self.vmx)
                        self.vm.set_gvmanalysis(self.gmx)
                        # Generate xref(s)
                        self.vm.create_xref()
                        self.vm.create_dref()
                    else:
                        CommandError("Cannot analyze VM instance (!)")
                else:
                    CommandError("Cannot load VM instance (!)")
        else:
            CommandError("classes.dex not found (!)")

    def do_operate(self, args):
        """
        := operate apk path_to_apk
        := operate dex path_to_classes.dex
        """
        try:
            if args.split()[0] == "apk":
                if args.split()[1]:
                    self.logger.log("info", "Loading : {} ...".format(args.split()[1].split("/")[-1]))
                    from androguard.core.bytecodes.apk import APK
                    self.apk = APK(args.split()[1])
                    if self.apk:
                        print(self.t.yellow("\n\t--> Loaded : {} (!)\n".format(args.split()[1].split("/")[-1])))
                        self.package = self.apk.get_package()
                        from core.brains.apk.components import Components
                        # Load activies, services, broadcast receivers, and
                        # content providers
                        self.components = Components(self.apk)
                        self.components.enumerate_components()
                        self.permissions = self.apk.get_permissions()
                        self.files = self.apk.get_files()
                        self.files_type = self.apk.get_files_types()
                        # Process virtual machine
                        self.process_vm()
                    else:
                        CommandError("APK not loaded (!)")
            else:
                CommandError("Unkown command (!)")
        except ImportError as e:
            CommandError(e.message)
        except IndexError as e:
            CommandError("Not enough arguments (!)")

    def do_surgical(self, args):
        """
        := surgical
        """

        try:
            if self.vm and self.vmx:
                from .surgical import Run
                run = Run(self.vm, self.vmx)
                run.prompt = self.t.yellow("(surgical) ")
                run.ruler = self.t.yellow("-")
                run.cmdloop()
            else:
                CommandError("classes.dex not loaded (!)")
        except Exception as e:
            CommandError(e.message)

    def do_attacksurface(self, args):
        """
        := attacksurface
        """
        try:
            if self.apk and self.components:
                self.logger.log("info", "Loading attacksurface module ...")
                from core.brains.apk.attacksurface import AttackSurface
                self.attack_surface = AttackSurface(self.apk, self.components)
                self.attack_surface.run()
        except ImportError as e:
            CommandError(e.message)

    def do_permissions(self, args):
        """
        := permissions list
        """
        try:
            if self.permissions:
                if args.split()[0] == "list":
                    self.logger.log("info", "Loading permissions ... \n")
                    for p in self.permissions:
                        print(self.t.yellow("\t--> {}".format(p)))
                    print("\n")
            else:
                CommandError("Permissions not found (!)")
        except Exception as e:
            CommandError(e.message)

    def do_files(self, args):
        """
        := files all
        := files assets
        := files libs
        := files res
        """
        try:
            if self.files:
                if args.split()[0]:
                    if args.split()[0] == "assets":
                        self.logger.log("info", "Loading files ... \n")
                        for f in self.files:
                            if f.startswith("assets"):
                                print(self.t.yellow("\t--> {}".format(f)))
                        print("\n")
                    elif args.split()[0] == "libs":
                        self.logger.log("info", "Loading files ... \n")
                        for f in self.files:
                            if f.startswith("lib"):
                                print(self.t.yellow("\t--> {}".format(f)))
                        print("\n")
                    elif args.split()[0] == "res":
                        self.logger.log("info", "Loading files ... \n")
                        for f in self.files:
                            if f.startswith("res"):
                                print(self.t.yellow("\t--> {}".format(f)))
                        print("\n")
                    elif args.split()[0] == "all":
                        self.logger.log("info", "Loading files ... \n")
                        for f in self.files:
                            print(self.t.yellow("\t--> {}".format(f)))
                        print("\n")
            else:
                CommandError("Files not populated (!)")
        except Exception as e:
            CommandError(e.message)

    def do_strings(self, args):
        """
        List and search for strings found in classes.dex

        := strings list
        := strings search
        """

        # Locals
        strings = None

        try:
            if args.split()[0] == "list":
                if self.vm:
                    strings = self.vm.get_strings()
                    if strings:
                        for s in strings:
                            print(self.t.cyan("--> {}".format(s.encode("utf-8"))))
                    else:
                        CommandError("Strings not found (!)")
                else:
                    CommandError("classes.dex not loaded (!)")
            elif args.split()[0] == "search":
                if self.vm:
                    strings = self.vm.get_strings()
                    if strings:
                        target = raw_input(self.t.yellow("\n\t--> Enter string : \n"))
                        for s in strings:
                            if target in s:
                                print(self.t.cyan("\t\t --> {}".format(s)))
                        print("\n")
                    else:
                        CommandError("Strings not found (!)")
                else:
                    CommandError("classes.dex not loaded (!)")
            else:
                CommandError("Command not found (!)")
        except Exception as e:
            # We might be see an exception like this:
            # 'utf8' codec can't decode byte 0xc0 in position 0: invalid start byte
            raise e
            CommandError(e.message)

    def do_components(self, args):
        """
        := components list
        """
        try:
            if args.split()[0] == "list":
                if self.apk:
                    self.logger.log("info", "Enumerating components ...\n")
                    if self.components.activities:
                        for a in self.components.activities:
                            print(self.t.yellow("\t--> activity : {}".format(a)))
                        print("\n")
                    if self.components.services:
                        for s in self.components.services:
                            print(self.t.yellow("\t--> service : {}".format(s)))
                        print("\n")
                    if self.components.receivers:
                        for r in self.components.receivers:
                            print(self.t.yellow("\t--> receiver : {}".format(s)))
                        print("\n")
                    if self.components.providers:
                        for r in self.components.providers:
                            print(self.t.yellow("\t--> provider : {}".format(s)))
                        print("\n")
                else:
                    CommandError("APK not loaded (!)")
            else:
                CommandError("Command not found (!)")
        except Exception as e:
            CommandError(e.message)

    def do_interact(self, args):
        """
        Drop into an interactive IPython session.

        := interact
        """
        try:
            if self.vm and self.vmx:
                from core.brains.interact.interact import Interact
                i = Interact(self.vm, self.vmx)
                i.run()
            else:
                CommandError("classes.dex not loaded (!)")
        except Exception as e:
            CommandError(e.message)

    def do_macro(self, args):
        """
        """
        return
