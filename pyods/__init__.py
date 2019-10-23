from .OnlineDisk import DiskImage, OpticalDrive
from .tools import list_images, list_optical_drives, get_local_ip
import cherrypy
import logging
import json
import os
import importlib
import datetime


search_config = [
    "/etc/pyods/config.json",
    "~/.pyods/config.json",
    "/opt/venvs/pyods/config/config.json"
]


#
# Monkey patch for JSON Serialisation
#
def _default(self, obj):
    if type(obj) == datetime.datetime:
        return obj.isoformat()
    try:
        out = getattr(obj.__class__, "serialise", _default.default)(obj)
    except:
        raise Exception("Cannot JSON Serialise object: " + obj.__class__.__name__)
    return out

from json import JSONEncoder
_default.default = JSONEncoder.default
JSONEncoder.default = _default


class Server:
    @property
    def disks(self):
        if self.drives is None or self.images is None:
            self.update()
        all = self.drives + self.images
        return {'disk%d' % i: d for i, d in enumerate(all)}

    @property
    def host(self):
        return self.config['host']

    @property
    def port(self):
        return self.config['port']

    def update(self):
        if self.images is None or self.drives is None:
            changed = True
            h = 0
        else:
            changed = False
            h = hash(tuple(self.images))

        self.images = [DiskImage(f) for f in list_images(self.config['root'])]

        if hash(tuple(self.images)) != h:
            changed = True

        try:
            if changed is False:
                h = hash(tuple(self.drives))
            self.drives = [OpticalDrive(f) for f in list_optical_drives()]
            if changed is False and hash(tuple(self.drives)) != h:
                changed = True
        except:
            self.drives = []

        if 'Bonjour' in self.plugins.keys() and changed:
            self.plugins['Bonjour'].update()

    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        logging.info("Using config file %s" % self.config_file_path)

        self.config = {
            "host": get_local_ip(),
            "port": 49152,
            "root": "/mnt/images"
        }

        try:
            with open(self.config_file_path) as f:
                config = json.loads(f.read())
            self.config.update(config)
        except:
            self.save_config()

        if not os.path.exists(self.config['root']):
            # Create the images path if possible, otherwise raise an error
            # but continue gracefully.
            pass

        self.images = None
        self.drives = None

        cherrypy.config.update({
            'server.socket_host': self.host,
            'server.socket_port': self.port
        })

        self.load_plugins()

    def load_plugins(self):
        logging.info("Loading plugins")
        files = os.listdir(os.path.join(os.path.dirname(__file__), "Plugins"))
        self.plugins = {}
        for f in files:
            if f.startswith('__'): continue

            module_name = "pyods.Plugins." + f[:-3]
            try:
                module = importlib.import_module(module_name)
                plugin = getattr(module, str(module.__plugin__))
                logging.info("Loaded plugin named " + module_name)
                self.plugins[plugin.__name__] = plugin(self)
            except:
                logging.exception("Cannot load plugin named " + module_name)
                continue

    def run(self):
        logging.info("Starting webserver")
        cherrypy.engine.start()
        cherrypy.engine.block()

    def stop(self):
        self.save_config()
        self.plugins = []
        cherrypy.engine.stop()

    def save_config(self):
        if os.access(self.config_file_path, os.W_OK):
            config_data = json.dumps(self.config, indent=4, sort_keys=True)
            with open(self.config_file_path, 'w') as f:
                f.write(config_data)


def find_config():
    w = None
    for f in search_config:
        f = os.path.expanduser(f)
        d = os.path.dirname(f)
        if os.path.exists(d):
            if os.path.exists(f):
                return f
            if os.access(d, os.W_OK):
                w = f
        elif os.access(os.path.dirname(d), os.W_OK):
            os.makedirs(d)
            w = f
    if w is None:
        logging.error("Cannot find suitable config path to write, create on in %s" % ' or '.join(search_config))
        raise Exception("No config file")
    return w


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] %(levelname)s:thread-%(threadName)-9s:%(message)s'
    )
    logging.info("Starting pyods remote disk server")
    config = find_config()
    s = Server(config)
    s.run()

if __name__ == '__main__':
    main()
