__author__ = 'alexander'
import os
import sys

from tornado.options import options, define, parse_command_line
import django.core.handlers.wsgi
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(_HERE)
sys.path.append(os.path.join(_HERE, '..'))
sys.path.append(os.path.join(_HERE, '../contrib'))
os.environ['DJANGO_SETTINGS_MODULE'] = "settings_m"

class BaseHandler(tornado.web.RequestHandler):
    wsgi_app = tornado.wsgi.WSGIContainer(
                django.core.handlers.wsgi.WSGIHandler())
    '''
    def initialize(self, fallback):
        self.fallback = fallback

    def prepare(self):
        self.fallback(self.request)
        self._finished = True
    '''
    def get(self):    
        ver = self.get_argument('version_test','')
        if ver:            
            ver="_"+'_'.join(ver.split(".")[0:1])
        os.environ['DJANGO_SETTINGS_MODULE'] = "settings"+ver
        return self.wsgi_app
        
class Application(tornado.web.Application):
    def __init__(self):
        
        wsgi_app = tornado.wsgi.WSGIContainer(
                django.core.handlers.wsgi.WSGIHandler())
        handlers = [
            
            (r"/test/.*", BaseHandler),
            ('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
            #('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
        ]
        tornado.web.Application.__init__(self, handlers)
        
    
    pass
def main(port):
    '''
    wsgi_app = tornado.wsgi.WSGIContainer(
        django.core.handlers.wsgi.WSGIHandler())
    tornado_app = tornado.web.Application(
        [('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
        ])
    server = tornado.httpserver.HTTPServer(tornado_app)
    '''
    server = tornado.httpserver.HTTPServer(Application())
    server.listen(port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main(int(sys.argv[1]))