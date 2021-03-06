
class SocketModel:
    values = {
        "android.net.LocalSocket": [
            "bind",
            "connect",
            "getInputStream",
            "getLocalSocketAddress",
            "isBound"
        ],
        "android.net.LocalSocketAddress": [
            "getName",
            "getNamespace",
        ],
        "android.net.LocalServerSocket": [
            "accept",
            "close",
            "getFileDescriptor",
            "getLocalSocketAddress"
        ],
        "java.net.ServerSocket": [
            "accept",
            "bind",
            "close",
            "getInetAddress",
            "getLocalPort",
            "getLocalSocketAddress",
            "isBound"
        ]
    }


class SocketModule(object):
    def __init__(self):
        self.name = "socket"
        self.model = SocketModel()
