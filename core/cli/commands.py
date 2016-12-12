from cmd2 import Cmd as Lobotomy
from core.logging.logger import Logger
from blessings import Terminal
from core.brains.utilities.util import Util


class CommandError(Exception):
    def __init__(self, message):
        self.logger = Logger()
        self.message = message
        self.logger.log("critical", self.message)


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
        Return True is classes.dex is found within the target APK
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
            CommandError(e)
        except IndexError as e:
            CommandError("Not enough arguments (!)")

    def do_surgical(self, args):
        """
        := surgical run
        """

        try:
            if self.vm and self.vmx:
                if args.split()[0] == "run":
                    from core.brains.surgical.api import Surgical
                    surgical = Surgical(self.vm, self.vmx, self.package)
                    surgical.factory()
                else:
                    CommandError("Unknown command (!)")
            else:
                CommandError("classes.dex not loaded (!)")
        except Exception as e:
            CommandError(e)

    def do_attacksurface(self, args):
        """
        := attacksurface run
        """
        try:
            if self.apk and self.components:
                if args.split()[0] == "run":
                    self.logger.log("info", "Loading attacksurface module ... ")
                    from core.brains.apk.attacksurface import AttackSurface
                    self.attack_surface = AttackSurface(self.apk, self.components)
                    self.attack_surface.run()
            else:
                CommandError("Components not found (!)")
        except ImportError as e:
            CommandError(e)

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
            CommandError(e)

    def do_files(self, args):
        """
        := files list
        := files list assets
        := files list libs
        := files list res
        """
        try:
            if self.files:
                if args.split()[0] == "list":
                    if args.split()[1] == "assets":
                        self.logger.log("info", "Loading files ... \n")
                        for f in self.files:
                            if f.startswith("assets"):
                                print(self.t.yellow("\t--> {}".format(f)))
                        print("\n")
                    elif args.split()[1] == "libs":
                        self.logger.log("info", "Loading files ... \n")
                        for f in self.files:
                            if f.startswith("lib"):
                                print(self.t.yellow("\t--> {}".format(f)))
                        print("\n")
                    elif args.split()[1] == "res":
                        self.logger.log("info", "Loading files ... \n")
                        for f in self.files:
                            if f.startswith("res"):
                                print(self.t.yellow("\t--> {}".format(f)))
                        print("\n")
                    else:
                        for f in self.files:
                            print(self.t.yellow("\t--> {}".format(f)))
                else:
                    self.logger.log("info", "Loading files ... \n")
                    for f in self.files:
                        print(self.t.yellow("\t--> {}".format(f)))
                    print("\n")
            else:
                CommandError("Files not populated (!)")
        except Exception as e:
            CommandError(e)

    def do_strings(self, args):
        """
        := strings list
        := strings search
        """
        try:
            if self.vm:
                strings = self.vm.get_strings()
                if strings:
                    if args.split()[0] == "list":
                        for s in strings:
                            print(self.t.yellow("\t{}".format(s.encode("utf-8"))))
                    if args.split()[0] == "search":
                        target = raw_input(self.t.yellow("\n\t--> Enter string : \n"))
                        for s in strings:
                            if target in s:
                                print(self.t.cyan("\t\t --> {}".format(s)))
                        print("\n")
                    else:
                        CommandError("Command not found (!)")
                else:
                    CommandError("Strings not found (!)")
            else:
                CommandError("Could not find classes.dex (!)")
        except Exception as e:
            CommandError(e)

    def do_components(self, args):
        """
        := components list
        """
        try:
            if self.apk:
                if args.split()[0] == "list":
                    self.logger.log("info",
                                    "Enumerating components ...\n".format(args.split()[0]))
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
        except Exception as e:
            CommandError(e)
