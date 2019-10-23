from zeroconf import ServiceInfo, Zeroconf
import socket
import logging

__plugin__ = "Bonjour"


class Bonjour:
    def __init__(self, server):
        self.server = server
        self.zeroconf = Zeroconf()
        self.info = None
        self.update()

    def update(self):
        self.remove()
        hostname = socket.gethostname()

        desc = {
            'sys': 'waMA=A4:BA:DB:E7:89:CD,adVF=0x4,adDT=0x3,adCC=1'
        }

        for (ident, disk) in self.server.disks.items():
            desc[ident] = 'adVN=%s,adVT=public.cd-media' % disk.label
            logging.info("Announcing disk \"%s\" as %s with name \"%s\"" % (disk.filename, ident, disk.label))

        self.info = ServiceInfo(
            "_odisk._tcp.local.",
            "%s._odisk._tcp.local." % hostname,
            addresses=[socket.inet_aton(self.server.host)],
            port=self.server.port,
            properties=desc,
        )

        self.add()

    def add(self):
        if self.info is None:
            return
        self.zeroconf.register_service(self.info)

    def remove(self):
        if self.info is None:
            return
        self.zeroconf.unregister_service(self.info)

    def __del__(self):
        self.remove()
        self.zeroconf.close()
