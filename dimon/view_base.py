#coding:utf-8
__author__ = 'zaddone'
import json
import re
import hashlib
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
        p['code']=code
        p['msg']=msg
        if _data:
            
            #p['msg']=msg
            p['list']=_data
        elif not p['msg']:
            
            p['msg']='Running error to not data'
        
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
    @property
    def redis_cache(self):
        return self.application.redis_cache
    
    def make_key(self, key):
        key= re.sub(ur"[^\w]", "", str(key) )
        return key[:64]

    @tornado.gen.coroutine
    def SendOrderMsg(self,phone=None,msg=''):
        if phone and msg:        
            client = tornado.httpclient.AsyncHTTPClient() 
            
            url = 'http://sdk.entinfo.cn:8060/z_mdsmssend.aspx'
            
            SN = 'SDK-SRF-010-00554'
            m = hashlib.md5()
            m.update(SN+'85-5C7d-')
            pwd = m.hexdigest().upper()
            data = {'sn':SN,
                        'pwd':pwd,
                        'mobile':phone,
                        'content':msg.encode('gb2312'),
                        }
            #res = urllib2.urlopen(url,urllib.urlencode(data)).read()
            url = tornado.httputil.url_concat(url, data)
            res = yield client.fetch(url)
            #return res
            if int(res) > 0:
                raise tornado.gen.Return(True)
                #return True
            else:
                raise tornado.gen.Return(False)
                #return res
                #return False
            
        else:
            raise tornado.gen.Return(False)
            #return  False
