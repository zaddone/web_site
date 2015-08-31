#coding:utf-8
__author__ = 'zaddone'
import time
import tornado.web
from update_code.view_base import baseHandler
class postHandler(baseHandler):
    def get(self):    
        self.return_style(template='post_page.html',_data=[])    
        #self.render("post_page.html", entries=[])
        
    @tornado.web.asynchronous
    def post(self):
        self.set_header("Content-Type", "text/plain")
        post_data = {}
        for key in self.request.arguments:
            value=self.get_arguments(key) 
            post_data[key] = value if len(value)>1 else value[0]     
            if post_data[key].isdigit():
                post_data[key]=int(post_data[key])
        self.write(self.user_post(post_data))
        self.finish() 
        
    def user_post(self,post_data,max_len=10):
        
        _code = 1
        _msg='Request is successful'
        if 'userid' in post_data:
            
            user_key=self.make_key(post_data['userid'])
            user_dict =self.cache.get(user_key)
            if type(user_dict)!=dict:
                user_dict={}
            
            time_s =str(int(time.time()))
            if time_s in user_dict:
                _code = 0
                _msg = "High frequency operation"
            user_dict[str(int(time.time()))]=post_data
            
            if len(user_dict)>max_len:
                _code = 0
                _msg =  "Submit a number of caps"
            else:
                try:
                    self.cache.set(user_key,user_dict,3600*24*30)
                except Exception,e:
                    _code = 0
                    _msg =  "memcache err: %s " % str(e)
            
            #return user_dict
        else:
            user_dict={}
            _code = 0
            _msg ="key userid not in arguments" 
            #self.cache.set(self.make_key(key),post_data,3600*24*7)
        return self.on_response(user_dict,msg=_msg,code=_code)
class showUserPostHandler(baseHandler):
    
    @tornado.web.asynchronous
    def get(self):
        userid = self.get_arguments('userid')
        user_dict={}
        if userid:    
            userid = self.make_key(userid)        
            user_dict = self.cache.get(userid)
        #self.write(user_dict)
        #user_dict = str(type(user_dict))
        
        times=self.get_arguments('times')
        if times:
            
            arr_dict={}
            for ti in times:
                if user_dict.has_key(ti):
                    arr_dict[ti]=user_dict.pop(ti)
                    
            if len(arr_dict)>0:
                self.cache.set(userid,user_dict,3600*24*30)
                self.return_style(template=None,_data=arr_dict)
                self.finish() 

        
        self.return_style(template=None,_data=user_dict)
        self.finish() 
        
        
