#coding:utf-8
__author__ = 'zaddone'
import json,re
import tornado.web


class baseHandler(tornado.web.RequestHandler):
    def return_callback_data(self,data):
        callback=self.get_argument('callback',None)
        if callback:
                res='%s(%s);' % (callback,json.dumps(data,separators=(',',':')))
        else:
            res=json.dumps(data,separators=(',',':'))
            
        return res
    def on_response(self, _data,msg='Request is successful',code=1):
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        p={}
        if _data:
            p['code']=1
            p['msg']=msg
            p['list']=_data
        else:
            p['code']=0
            p['msg']='Running error to %s' % self.sh_file
        
            
        return self.return_callback_data(p)

    def return_style(self,template=None,_data={}):
        if not template:
            template=self.get_argument('template',None)
        if template:
            self.render(template, data = _data)
        else:
            self.write(self.on_response(_data))
    @property
    def db(self):
        return self.application.db
    
    @property
    def cache(self):
        return self.application.cache
    
    def make_key(self, key):
        key= re.sub(ur"[^\w]", "", str(key) )
        return key[:64]

        
