from cmd2 import Cmd as SurgicalCmd
from core.logging.logger import Logger
from blessings import Terminal
from datetime import datetime
from core.brains.utilities.util import Util
from core.brains.surgical.modules.intent import IntentModule
from core.brains.surgical.modules.zip import ZipModule
from core.brains.surgical.modules.socket import SocketModule
from pygments import highlight
from pygments.lexers import JavaLexer
from pygments.formatters import TerminalFormatter


class SurgicalError(Exception):
    def __init__(self, message):
        self.logger = Logger()
        self.message = message
        self.logger.log("critical", "Surgical : {}".format(self.message))


class Run(SurgicalCmd):
    def __init__(self, vm, vmx):
        SurgicalCmd.__init__(self)
        self.logger = Logger()
        self.t = Terminal()
        self.u = Util()
        self.vm = vm
        self.vmx = vmx
        self.methods = self.vm.get_methods()
        self.intent = IntentModule()
        self.zip = ZipModule()
        self.socket = SocketModule()
        self.modules = [m for m in self.zip, self.intent, self.socket]
        self.target_module = None
        self.methods_api_usage = list()

    def do_modules(self, args):
        """
        List and select target API modules.

        := modules list
        := modules select
        """

        # Locals
        selection = None

        try:
            if args.split()[0] == "list":
                if self.modules:
                    print("\n")
                    for m in self.modules:
                        if m:
                            print(self.t.cyan("\t--> {}".format(m.name)))
                    print("\n")
            if args.split()[0] == "select":
                if self.modules:
                    selection = raw_input(self.t.yellow("[{}] ".format(datetime.now())) + "Select module : ")
                    for m in self.modules:
                        if m:
                            if selection == m.name:
                                self.target_module = m
                                self.logger.surgical_log("info", "{} module selected (!)".format(m.name))
        except Exception as e:
            SurgicalError(e.message)

    def do_api(self, args):
        """
        List and select methods from a given loaded API module

        := api list
        := api select
        := api analyzed list
        := api analyzed select
        """

        # Locals
        class_selection = None
        method_selection = None
        surgical_lib = None

        try:
            # List the available API methods from the target module
            if args.split()[0] == "list":
                if self.target_module:
                    print("\n")
                    for k, v in self.target_module.model.values.items():
                        print("\n")
                        for m in v:
                            print(self.t.cyan("\t--> {} : {} : {}"
                                              .format(self.target_module.name,
                                                      k.split(".")[-1], m)))
                    print("\n")
                else:
                    self.logger.surgical_log("info", "Target module has not been loaded (!)")
            # Select an API method from the target module
            elif args.split()[0] == "select":
                if self.target_module:
                    # TODO Consider building a wrapper around raw_input()
                    class_selection = raw_input(self.t.yellow("[{}] ".format(datetime.now())) + "Select class : ")
                    method_selection = raw_input(self.t.yellow("[{}] ".format(datetime.now())) + "Select method : ")
                    for k, v in self.target_module.model.values.items():
                        # This is so we can support classes with identical
                        # method names --> Ex: java.util.zip.ZipFile
                        if class_selection == k.split(".")[-1]:
                            print(k)
                            for m in v:
                                if m == method_selection:
                                    self.logger.surgical_log("info",
                                                             "Analyzing ...")
                                    from core.brains.surgical.lib.libsurgical import SurgicalLib
                                    # Begin processing and return the results
                                    # from the selected api
                                    surgical_lib = SurgicalLib(self.target_module,
                                                               self.vmx,
                                                               self.vm,
                                                               k,
                                                               method_selection,
                                                               self.methods)
                                    # methods_api_usage will contain a list of
                                    # tuples
                                    self.methods_api_usage = surgical_lib.search()
                                else:
                                    self.logger.surgical_log("warn",
                                                             "Method not found (!)")
            # Analyze the processed method list
            elif args.split()[0] == "analyzed":
                # List the methods that have been processed
                if args.split()[1] == "list":
                    if self.methods_api_usage:
                        print("\n")
                        for m in self.methods_api_usage:
                            print(self.t.cyan("\t--> {} -> {} "
                                              .format(m[0].class_name,
                                                      m[0].name)))
                        print("\n")
                    else:
                        SurgicalError("API usage not found (!)")
                # Select from the processed method list
                elif args.split()[1] == "select":
                    if self.methods_api_usage:
                        selection = raw_input(self.t.yellow("[{}] ".format(datetime.now())) + "Select method : ")
                        for m in self.methods_api_usage:
                            if selection == m[0].name:
                                print("\n")
                                print(self.t.cyan("\t--> Class : {}"
                                                  .format(m[0].class_name)))
                                print(self.t.cyan("\t\t--> Method : {}"
                                                  .format(m[0].name)))
                                print(self.t.cyan("\t\t\t --> XREFS ###########"))
                                self.u.print_xref("T", m[1].method.XREFto.items)
                                self.u.print_xref("F", m[1].method.XREFfrom.items)
                                print("\n")
                                print(highlight(m[2],
                                                JavaLexer(),
                                                TerminalFormatter()))
                    else:
                        SurgicalError("API usage not found (!)")
        except Exception as e:
            SurgicalError(e.message)
