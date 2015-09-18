#coding:utf-8
__author__ = 'zaddone'
import time
import random
import tornado.web
import tornadoredis
#import re
from view_base import baseHandler
c = tornadoredis.Client()
class postHandler(baseHandler):
    def get(self):
        sign = self.get_arguments('sign') 
        if len(sign)>0:
            if sign[0]=='up':
                self.return_style(template='sign_up.html',_data=[])
            elif  sign[0]=='verify':
                self.return_style(template='verify.html',_data=[])
        self.return_style(template='sign_in.html',_data=[])   
        #self.render("post_page.html", entries=[])
        
    #@tornado.web.asynchronous
    #@tornado.gen.engine
    @tornado.gen.coroutine
    def post(self):
        self.set_header("Content-Type", "text/plain")
        post_data = {}
        for key in self.request.arguments:
            value=self.get_arguments(key) 
            post_data[key] = value if len(value)>1 else value[0]     
            if type(post_data[key])==int and post_data[key].isdigit():
                post_data[key]=int(post_data[key])
        
        self.write(self.Handle_checkcode(post_data))
        #self.write(post_data)
        '''
        if 'func' in post_data:
            self.write(self.post_function(post_data,keys=post_data['func']))
        else:
            self.write(post_data)
        self.finish()
        '''
    
    @tornado.gen.coroutine
    def Handle_checkcode(self,**kwargs):
        phone =  kwargs.get('phone',None)
        #ph=re.compile('^1[358]\d{9}$|^147\d{8}')
        #ph = re.compile('^\d{13}')
        if phone:

            checkcode = random.randint(100000,999999)
            msg = u'您好,您的验证码%s,10分钟内有效,请及时校验【小日子】'%checkcode
            sns_send = yield self.SendOrderMsg(phone,msg)
            if sns_send:
                #foo = yield tornado.gen.Task(self.redis_cache.get, 'foo')
                ver = yield tornado.gen.Task(self.redis_cache.set, 'verify_%s' % str(phone),{'checkcode':str(checkcode)},60*10)
                #self.cache.set('verify_%s' % str(phone),{'checkcode':str(checkcode)},60*10)
                if ver:
                    raise tornado.gen.Return(self.on_response({"phone":phone},msg=u'验证码发送成功',code=1))
                
            #else:
            raise tornado.gen.Return(self.on_response({"phone":phone},msg=u'验证码发送失败',code=0))
                
        else:
            raise tornado.gen.Return(self.on_response({},msg=u'手机号为空',code=0))
    def verify_code(self,checkcode,phone):        
        if checkcode and phone:
            key_name='verify_%s' % str(phone)
            ver_code = yield tornado.gen.Task(self.redis_cache.get, key_name)
            #ver_code = self.cache.get(key_name)
            if ver_code and  ver_code.get('checkcode',None):
                if checkcode.lower() == ver_code['checkcode'].lower():
                    self.cache.delete(key_name)
                    c.delete()
                    return True                    
        return False
    
    def Handle_signUp(self,**kwargs):

        key_val={}
        checkcode =  kwargs.pop('checkcode')
        
        if not checkcode:
            return self.on_response(key_val,msg='Not checkcode',code=0)
        
        phone =  kwargs.get('phone',None)
        if not phone:
            return self.on_response(key_val,msg='Not phone',code=0)
        
        if self.verify_code(checkcode,phone):
            key_name='signup_%s' % str(phone)
            key_name_list='signup_list'
            key_val_list =self.cache.get(key_name_list)
            if not key_val_list:
                key_val_list={}
            
            key_val_list[key_name]=str(int(time.time()))
            '''
            key_val =self.cache.get(key_name)
            if key_val:
                _code = 0
                _msg='Data modification'
            '''
            self.cache.set(key_name_list,key_val_list,3600*24*30)
            self.cache.set(key_name,kwargs,3600*24*30)
            return self.on_response(key_val,msg='Request is successful',code=0)
        
        return self.on_response(key_val,msg='Request is fail',code=0)
        
    def Handle_userpost(self,**kwargs):
        _code = 1
        _msg='Request is successful'
        max_len=10
        if 'userid' in kwargs:
            user_key=self.make_key(kwargs['userid'])
            user_dict =self.cache.get(user_key)
            if type(user_dict)!=dict:
                user_dict={}
            
            time_s =str(int(time.time()))
            if time_s in user_dict:
                _code = 0
                _msg = "High frequency operation"
            user_dict[str(int(time.time()))]=kwargs
            
            if len(user_dict)>max_len:
                _code = 0
                _msg =  "Submit a number of caps"
            else:
                try:
                    self.cache.set(user_key,user_dict,3600*24*30)
                except Exception,e:
                    _code = 0
                    _msg =  "memcache err: %s " % str(e)
        else:
            user_dict={}
            _code = 0
            _msg ="key userid not in arguments"
            #self.cache.set(self.make_key(key),post_data,3600*24*7)
        return self.on_response(user_dict,msg=_msg,code=_code)
    def post_function(self,post_data,func='',max_len=10):
        
        _code = 1
        _msg='Request is successful'
        _Handle = getattr(self, 'Handle_%s' % func, None)
        if _Handle:
            
            user_dict=_Handle(post_data)
            return self.on_response(user_dict,msg=_msg,code=_code)
        else:
            self.write(post_data)
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
        
        
