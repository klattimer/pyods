import cherrypy
import re
import os
from datetime import datetime
import logging
from pyods.OnlineDisk import OnlineDiskState

__plugin__ = "ODS"


class ODS:
    exposed = True
    path = '/'
    config = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [
                ('Content-Type', 'application/octet-stream'),
                ('Server', 'ODS/1.0')
            ]
        }
    }

    def __init__(self, server):
        self.server = server
        self._re_range = re.compile('bytes=(\d*?)-(\d*)')
        cherrypy.tree.mount(self, self.__class__.path, self.__class__.config)

    def GET(self, disk, fork=None, misc=None):
        """
        A get request is sent for reading a "chunk" of a disk using a supplied byte
        range.
        """
        if cherrypy.request.headers['user-agent'] != 'CCURLBS::readDataFork':
            logging.debug("User-Agent: " + str(cherrypy.request.headers['user-agent']))
            raise cherrypy.HTTPError(403)

        (disk, extension) = os.path.splitext(os.path.basename(disk))

        try:
            disk = self.server.disks[disk]
        except:
            raise cherrypy.HTTPError(404, "Disk not found")

        try:
            range = cherrypy.request.headers['range']
            start, end = self._re_range.findall(range)[0]
            start, end = int(start), int(end)
        except:
            logging.exception("range: " + str(range))
            raise cherrypy.HTTPError(500, "Range decode error: " + str(range))

        if disk.state == OnlineDiskState.READY:
            data = disk.read(start, end)
        else:
            raise cherrypy.HTTPError(404, 'Device not ready')

        cherrypy.response.headers['Content-Range'] = 'bytes %d-%d/%d' % (start, end, disk.size)
        return data

    def HEAD(self, disk, fork=None, misc=None):
        """
        Return the header indicating the disk size in bytes and the current date/time
        """
        if cherrypy.request.headers['user-agent'] != 'CCURLBS::statImage':
            logging.debug("User-Agent: " + str(cherrypy.request.headers['user-agent']))
            raise cherrypy.HTTPError(403)

        (disk, extension) = os.path.splitext(os.path.basename(disk))

        try:
            disk = self.server.disks[disk]
        except:
            raise cherrypy.HTTPError(404, "Disk not found")

        cherrypy.response.headers['Date'] = datetime.utcnow().isoformat()
        cherrypy.response.headers['Accept-Ranges'] = 'bytes'
        cherrypy.response.headers['Content-Length'] = disk.size
