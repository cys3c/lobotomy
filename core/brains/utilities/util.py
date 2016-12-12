from blessings import Terminal

class Util(object):
    def __init__(self):
        self.t = Terminal()

    @staticmethod
    def read(filename, binary=True):
        with open(filename, 'rb' if binary else 'r') as f:
            return f.read()

    def print_xref(self, tag, items):
        for i in items:
            print(self.t.cyan("\t\t\t\t{}: {} {} {} {}".format(
                tag,
                i[0].get_class_name(),
                i[0].get_name(),
                i[0].get_descriptor(),
                " ".join("%x" % j.get_idx() for j in i[1]))))
