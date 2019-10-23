import cherrypy
import logging
import os

__plugin__ = "ImageAPI"


class ImageAPI:
    exposed = True
    path = '/images'
    config = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.json_out.on': True
        }
    }

    def __init__(self, server):
        self.server = server
        cherrypy.tree.mount(self, self.__class__.path, self.__class__.config)

    def POST(self, image):
        # Upload image to the image bucket
        size = 0
        success = False
        try:
            ext = os.path.splitext(image.filename)[1][1:].lower()
            if ext not in ['img', 'dmg', 'iso']:
                raise cherrypy.HTTPError(403, "Unsupported image file")
            path = os.path.join(self.server.config['root'], image.filename)
            with open(path, "wb") as f:
                while True:
                    data = image.file.read(8192)

                    if not data:
                        break

                    size += len(data)
                    f.write(data)
            self.server.update()
            success = True
        except:
            logging.exception("Failed to store upload")

        return {
            'size': size,
            'success': success
        }

    def GET(self):
        return self.server.disks

    def DELETE(self, image_name):
        # self.server.disks[image_name].erase()
        pass
