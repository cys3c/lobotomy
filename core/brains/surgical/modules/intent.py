from androguard.decompiler.dad import decompile
from pygments import highlight
from pygments.lexers import JavaLexer
from pygments.formatters import TerminalFormatter
from core.logging.logger import Logger
from blessings import Terminal
from core.brains.utilities.util import Util
from datetime import datetime

class IntentModel:
    values = {
        "android.content.Intent" : [
            "parseUri",
            "getAction",
            "getBundleExtra",
            "getClipData",
            "getComponent",
            "getData",
            "getDataString",
            "getExtras",
            "getIntent",
            "getPackage",
            "getScheme",
            "getSelector",
        ]
    }


class IntentModule(object):
    def __init__(self, vm, vmx, package):
        self.name = "intent"
        self.model = IntentModel()
