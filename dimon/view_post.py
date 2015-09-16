#coding:utf-8
__author__ = 'zaddone'
import time
import tornado.web
#import re
from view_base import baseHandler
class postHandler(baseHandler):
    def get(self):
        sign = self.get_arguments('sign') 
        if len(sign)>0 and sign[0]=='up':
            self.return_style(template='sign_up.html',_data=[])
         
        else:
            self.return_style(template='sign_in.html',_data=[])   
        #self.render("post_page.html", entries=[])
        
    @tornado.web.asynchronous
    def post(self):
        self.set_header("Content-Type", "text/plain")
        post_data = {}
        for key in self.request.arguments:
            value=self.get_arguments(key) 
            post_data[key] = value if len(value)>1 else value[0]     
            if type(post_data[key])==int and post_data[key].isdigit():
                post_data[key]=int(post_data[key])
                
        #self.write(post_data)
        if 'func' in post_data:
            self.write(self.post_function(post_data,keys=post_data['func']))
        else:
            self.write(post_data)
        self.finish()
    
    def Handle_checkcode(self,**kwargs):
        phone =  kwargs.get('phone',None)
        #ph=re.compile('^1[358]\d{9}$|^147\d{8}')
        #ph = re.compile('^\d{13}')
        if phone:
 
            import random
            #url = 'http://sdk.entinfo.cn:8060/z_mdsmssend.aspx'
            checkcode = random.randint(100000,999999)
            msg = u'您好,您的验证码%s,10分钟内有效,请及时校验【小日子】'%checkcode
            if self.SendOrderMsg(phone,msg):
                self.cache.set('verify_%s' % str(phone),{'checkcode':str(checkcode)},60*10)
                return self.on_response({"phone":phone},msg=u'验证码发送成功',code=1)
                
            else:
                return self.on_response({"phone":phone},msg=u'验证码发送失败',code=0)
                
        else:
            return self.on_response({},msg=u'手机号为空',code=0)
    def verify_code(self,checkcode,phone):        
        if checkcode and phone:
            ver_code = self.cache.get('verify_%s' % str(phone))
            if ver_code and  ver_code.get('checkcode',None):
                if checkcode.lower() == ver_code['checkcode'].lower():
                    return True                    
        return False
    
    def Handle_signUp(self,**kwargs):
        _code = 1
        _msg='Request is successful'
        checkcode =  kwargs.get('checkcode',None)
        if not checkcode:
            _code = 0
            _msg='Not checkcode'
        phone =  kwargs.get('phone',None)
        if not phone:
            _code = 0
            _msg='Not phone'
        if self.verify_code(checkcode,phone):
            key_name='verify_%s' % str(phone)
            
            

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
        
        
