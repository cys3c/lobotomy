from androguard.decompiler.dad import decompile
from pygments import highlight
from pygments.lexers import JavaLexer
from pygments.lexers.dalvik import SmaliLexer
from pygments.formatters import TerminalFormatter
from core.logging.logger import Logger
from blessings import Terminal
from datetime import datetime

class WebModel:
    values = {
        "android.webkit.WebView" : [
            "addJavascriptInterface",
            "evaluateJavascript",
            "loadData",
            "loadDataWithBaseURL",
            "loadUrl"
        ],

        "android.webkit.WebViewClient": [
            "shouldInterceptRequest",
            "shouldOverrideUrlLoading"
        ]
    }


class WebModule(object):
    def __init__(self, vm, vmx, package):
        self.name = "web"
        self.logger = Logger()
        self.t = Terminal()
        self.package = package
        self.vm = vm
        self.vmx = vmx
        self.methods = self.vm.get_methods()
        self.package = package
        self.model = WebModel()


    def process_methods(self, found_methods):
        """
        Process and return a unique and analyzed list of methods based on usage
        findings

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


    def analyze_method(self, processed):
        """
        Provide the ability to analyze each processed method that contains
        the specific API usage.

        Args:
            param1 : Processed methods represented as a tuple
                     (encoded_method, analyzed_method, source_code)

        Returns:
            None
        """

        # TODO There needs to be more fine grained control over methods with the same name,
        # but different classes

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
                        print(self.t.cyan("\t--> Method : {}".format(p[0].name)))
                        print("\n")
                        # Print code_object
                        #print(p[0].code.code.pretty_show(p[1]))
                        print("\n")
                        # Print source_code
                        print("\t" + highlight(p[2], JavaLexer(), TerminalFormatter()))


    def run(self):
        """
        Run the surgical Intent module.

        Args:
            None

        Returns:
            None
        """

        selection = None
        found_methods = list()
        paths = None

        for k, v in self.model.values.items():
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
                for k, v in self.model.values.items():
                    if k:
                        for m in v:
                            print(self.t.cyan("\t--> {}".format(m)))
                print("\n")
            else:
                for k, v in self.model.values.items():
                    if k:
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
                                            self.analyze_method(processed)
                                    else:
                                        self.logger.log("warn", "Error with processing results (!)")
                                else:
                                    self.logger.log("warn", "Zero results found (!)")
