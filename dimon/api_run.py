#coding:utf-8
__author__ = 'zaddone'

import sys,os
import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
import torndb
import memcache
import tornadoredis

from tornado.options import define, options

from view_post import postHandler,dbCheck,mongotest


define("memcache_ip", default="127.0.0.1:11211", help="memcache ip")
define("mysql_host", default="10.10.1.163:3306", help="database host")
define("mysql_database", default="user_center", help="database name")
define("mysql_user", default="usercenter", help="database user")
define("mysql_password", default="ghk*LoY5,;:/?", help="database password")

define("port", default=8888, help="run on the given port", type=int)
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            
            (r"/dimon/post/",postHandler),
            #(r"/dimon/get/",showUserPostHandler),
            (r"/dimon/check/",dbCheck),
            (r"/dimon/mongotest/",mongotest),
            
            
            
            
        ]
        
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "/"),
            api_title=u"xiaorizi  api",
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        self.CONNECTION_POOL = tornadoredis.ConnectionPool(max_connections=500,
                                              wait_for_available=True)
        self.redis_cache = tornadoredis.Client(connection_pool=self.CONNECTION_POOL)
        self.cache = memcache.Client([options.memcache_ip])
        self.db = torndb.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password)
        


def main(port):
    tornado.options.parse_command_line()
    try:
        
        http_server = tornado.httpserver.HTTPServer(Application())
        http_server.listen(port)
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.close()

if __name__ == "__main__":
    try:
        main(int(sys.argv[1]))
    except:
        main(options.port)
