#coding:utf-8
__author__ = 'zaddone'
import os
import json
import tornado.web
from update_code.view_base import baseHandler
class viewHandler(baseHandler):
    @tornado.web.asynchronous
    def get(self):
        self.sh_path=self.get_argument('sh_path',None)
        if not self.sh_path:
            self.sh_path='/data/web/user_center_git'
        _file=self.get_argument('sh_file',None)
        if not _file:
            _file ='%s/update_file.sh' % self.sh_path
        else:
            _file ='%s/%s.sh' % (self.sh_path,_file)
        #self.write(self.sh_path)
        msg = self.on_response(_data=self.find_sh_file(sh_file=_file))
        self.write(msg)
        self.finish()


    def find_sh_file(self,sh_file='/data/web/user_center_git/update_file.sh'):
        self.sh_file=sh_file
        if os.path.isfile(sh_file):
            _file = os.popen(sh_file)
            return _file.read()
        return False

        
        

                
                