from core.logging.logger import Logger
from androguard.decompiler.dad import decompile
from pygments import highlight
from pygments.lexers import JavaLexer
from pygments.formatters import TerminalFormatter
from . modules.web import WebModule
from . modules.intent import IntentModule
from core.brains.utilities.util import Util
from blessings import Terminal
from datetime import datetime


class Surgical(object):

    def __init__(self, vm, vmx, package):
        self.logger = Logger()
        self.t = Terminal()
        self.u = Util()
        self.vm = vm
        self.vmx = vmx
        self.package = package
        self.methods = self.vm.get_methods()
        self.logger.log("info", "Loading modules ...\n")
        self.web = WebModule(self.vm, self.vmx, self.package)
        self.intent = IntentModule(self.vm, self.vmx, self.package)
        self.modules = [m for m in self.web, self.intent]
        self.target_module = None


    def factory(self):
        """
        The surgical module's main factory function.  Based on the user's selection,
        this function will return an instance of selected module, and set it as
        the target module.  This instance will be used by the run() function,
        when it is called.

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
                        self.target_module = m
                        self.run()


    def process_methods(self, found_methods):
        """
        Process and return a unique and analyzed list of methods based on usage
        findings.

        Args:
            param1: Discovered methods

        Returns:
            return: Processed methods
        """
        seen = set()
        unique = list()
        processed = list()
        # Sort the list of methods based on their owner class
        for m in found_methods:
            if m.get_class_name() not in seen:
                unique.append(m)
                seen.add(m.get_class_name())
        for u in unique:
            # If the method contains code, then decompile it
            if u.get_code():
                analyzed = self.vmx.get_method(u)
                src = decompile.DvMethod(analyzed)
                src.process()
                processed.append((u, analyzed, src.get_source()))
            else:
                analyzed = self.vmx.get_method(u)
                processed.append((u, analyzed, None))
        # Return the processed list of methods
        return processed


    def analyze_methods(self, processed):
        """
        Provide the ability to analyze each processed method that contains
        the specific API usage.  For each analyzed method, the
        function will print out the class name, method name, XREF(s), and source

        Args:
            param1 : Processed methods represented as a tuple
                     (encoded_method, analyzed_method, source_code)

        Returns:
            None
        """

        # TODO There needs to be more fine grained control over methods with the same name,
        # but different classes

        # Locals
        selection = None

        for p in processed:
            print(self.t.cyan("\t--> {} -> {} ".format(p[0].class_name, p[0].name)))
        print("\n")
        while True:
            self.logger.log("info", "Enter 'back' to return")
            selection = raw_input(self.t.green("[{}] ".format(datetime.now())) +
                                  self.t.yellow("Select method : "))
            if selection == "back":
                # Break the loop and return to the API method selection menu
                break
            elif selection == "list":
                # Print the loaded method list
                print("\n")
                for p in processed:
                    print(self.t.cyan("\t--> {} -> {} ".format(p[0].class_name, p[0].name)))
                print("\n")
            else:
                for p in processed:
                    if selection == p[0].name:
                        print("\n")
                        # Print class_name
                        print(self.t.cyan("\t--> Class : {}".format(p[0].class_name)))
                        # Print method_name
                        print(self.t.cyan("\t\t--> Method : {}".format(p[0].name)))
                        print(self.t.cyan("\t\t\t --> XREFS ###########"))
                        self.u.print_xref("T", p[1].method.XREFto.items)
                        self.u.print_xref("F", p[1].method.XREFfrom.items)
                        # Print code_object
                        #print(p[0].code.code.pretty_show(p[1]))
                        print("\n")
                        # Print source_code
                        print(highlight(p[2], JavaLexer(), TerminalFormatter()))


    def run(self):
        """
        Run the target surgical module.

        Args:
            None

        Returns:
            None
        """

        # Locals
        selection = None
        found_methods = list()
        paths = None

        for k, v in self.target_module.model.values.items():
            if k:
                # Print the loaded method list
                self.logger.log("info", "Loading target methods ...\n")
                for m in v:
                    print(self.t.cyan("\t--> {}".format(m)))
                print("\n")
        while True:
            self.logger.log("info", "Enter 'back' to return to the main surgical module menu")
            selection = raw_input(self.t.green("[{}] ".format(datetime.now())) +
                                  self.t.yellow("Select method : "))
            # Break the loop and return to the main surgical module menu
            if selection == "back":
                break
            elif selection == "list":
                # Print the loaded method list
                print("\n")
                for k, v in self.target_module.model.values.items():
                    if k:
                        for m in v:
                            print(self.t.cyan("\t--> {}".format(m)))
                print("\n")
            else:
                for k, v in self.target_module.model.values.items():
                    for m in v:
                        if m == selection:
                            self.logger.log("info", "Searching ...")
                            # If the selected method is in the API list, search for it in all tainted_packages
                            paths = self.vmx.get_tainted_packages().search_methods(k, selection, ".")
                            if paths:
                                self.logger.log("info", "Found usage (!)")
                                for p in paths:
                                    # For path in tainted_paths populated a list of methods with the target
                                    # API usage
                                    for method in self.methods:
                                        # Name of the method
                                        if method.get_name() == p.get_src(self.vm.get_class_manager())[1]:
                                            # Method's class
                                            if method.get_class_name() == p.get_src(self.vm.get_class_manager())[0]:
                                                found_methods.append(method)
                                # If we have a populated list of found methods, process them
                                if found_methods:
                                    self.logger.log("info", "Processing ...")
                                    # Return a unique and analyzed list of methods that were found with API usage
                                    processed = self.process_methods(found_methods)
                                    print(self.t.yellow("\n\t--> Finished processing (!)\n".format(m)))
                                    if processed:
                                        # If the method has been processed, then analyze it
                                        self.analyze_methods(processed)
                                else:
                                    self.logger.log("warn", "Error with processing results (!)")
                            else:
                                self.logger.log("warn", "Zero results found (!)")
                        else:
                            self.logger.log("warn", "Method not found (!)")
