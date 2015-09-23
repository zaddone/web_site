#coding:utf-8
__author__ = 'zaddone'
import time
import json
import random
import tornado.web
#from common import send_mail

#import re
from view_base import baseHandler
from emailqueue.queues import MongoDbEmailQueue
#c = tornadoredis.Client()
recipient_addrs = 'zaddone@qq.com'
smtp_user = 'zl.feng@xiaorizi.me'
smtp_password = '520512fzl520512'

# Create the email queue.
email_queue = MongoDbEmailQueue(
    smtp_host='smtp.exmail.qq.com',
    smtp_port=25,
    smtp_user=smtp_user,
    smtp_password=smtp_password,
    mongodb_uri='mongodb://localhost:27017',
    mongodb_collection='email_queue',
    mongodb_database='email_db',
    queue_maxsize=0
)

class dbCheck(baseHandler):
    @tornado.gen.coroutine
    def get(self):
        keys_name = self.get_arguments('keys_name') 
        if len(keys_name)>0:
            arr = {'keys_name':keys_name[0]}
            k=yield self.keysList(**arr)
            arr = yield self.getKeysList(*k)
            
            self.write(self.on_response(arr,msg='Request is successful',code=0))
        else:
            self.return_style(template='sign_in.html',_data={})

    @tornado.gen.coroutine
    def keysList(self,**kwargs):
        #signup_
        keys_name =  kwargs.get('keys_name',None)
        keys_list={}
        if keys_name:
            keys_list = yield tornado.gen.Task(self.redis_cache.keys, '%s_*' % str(keys_name))
            raise tornado.gen.Return(keys_list)
        raise tornado.gen.Return(keys_list)

    @tornado.gen.coroutine
    def getKeysList(self,*args):
        db_list=[]
        if args:
            db_list = yield tornado.gen.Task(self.redis_cache.mget, args)
            new_list=[]
            for db in db_list:
                new_list.append(json.loads(db))
            db_list = new_list
        raise tornado.gen.Return(db_list)
    
class postHandler(baseHandler):
    @tornado.gen.coroutine
    def get(self):
        sign = self.get_arguments('sign') 
        _da={}

        if len(sign)>0:
            if sign[0]=='up':
                _da['city']=yield self.get_db_city()
            phone =  self.get_arguments('phone')
            if len(phone) > 0:
                _da['phone']=phone[0]
                try:
                    ver = yield tornado.gen.Task(self.redis_cache.get, 'signin_%s' % str(_da['phone']))
                except:
                    ver = None
                test =  self.get_arguments('test')
                if ver or len(test):
                    try:
                        _da['info']=  yield self.keysShow('signup_%s' % str(_da['phone']))
                    except:
                        pass
            _template ='%s.html' % sign[0]
            self.return_style(template=_template , _data=_da)
        else:
            self.return_style(template='verify.html',_data={})   


    @tornado.gen.coroutine
    def post(self):
        self.set_header("Content-Type", "text/plain")
        post_data = self.get_arg()

        
        k =yield self.post_function(post_data,func=post_data.pop('func'))

        self.write(k)

    def get_arg(self):
        post_data = {}
        for key in self.request.arguments:
            value=self.get_arguments(key) 
            post_data[key] = value if len(value)>1 else value[0]     
            if type(post_data[key])==int and post_data[key].isdigit():
                post_data[key]=int(post_data[key])
        return post_data

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
                che = json.dumps({'checkcode':str(checkcode)})
                ver = yield tornado.gen.Task(self.redis_cache.set, 'verify_%s' % str(phone),che,60*10)
                #self.cache.set('verify_%s' % str(phone),{'checkcode':str(checkcode)},60*10)
                if ver:
                    raise tornado.gen.Return(self.on_response({"phone":phone},msg=u'验证码发送成功',code=1))
                
            #else:
            raise tornado.gen.Return(self.on_response({"phone":phone},msg=u'验证码发送失败',code=0))
                
        else:
            raise tornado.gen.Return(self.on_response({},msg=u'手机号为空',code=0))
    @tornado.gen.coroutine
    def keysShow(self,keys_name):
        #signup_
        #keys_name =  kwargs.get('keys_show',None)
        keys_list={}
        if keys_name:
            keys_list = yield tornado.gen.Task(self.redis_cache.get, '%s' % str(keys_name))
                        
            raise tornado.gen.Return(json.loads(keys_list))
        raise tornado.gen.Return(keys_list)
    
    @tornado.gen.coroutine
    def Handle_verify(self,**kwargs): 
        checkcode=kwargs.get('checkcode',None)
        phone  = kwargs.get('phone',None)
        ver = yield self.verify_code(checkcode,phone)
        if ver:
            res=True
            '''
            key_name='verify_%s' % str(phone)
            res = yield tornado.gen.Task(self.redis_cache.delete, key_name)
            '''
            if res:
                
                _val = yield self.keysShow('signup_%s' % str(phone))
                if _val:
                    ver = yield tornado.gen.Task(self.redis_cache.set, 'signin_%s' % str(phone),str(time.time()),24*3600)
                    
                    raise tornado.gen.Return(self.on_response(_val,msg=u'登录成功',code=1))
                
                raise tornado.gen.Return(self.on_response({"phone":phone},msg=u'验证成功',code=1))
        raise tornado.gen.Return(self.on_response({"phone":phone,"checkcode":checkcode},msg=u'验证失败！',code=0))
     
    @tornado.gen.coroutine
    def verify_code(self,checkcode,phone):
        if checkcode and phone:
            key_name='verify_%s' % str(phone)
            ver_code = yield tornado.gen.Task(self.redis_cache.get, key_name)
            if ver_code:
                ver_code =json.loads(ver_code)
                if  checkcode.lower() == ver_code.get('checkcode',None).lower():
                    raise tornado.gen.Return( True)
        raise tornado.gen.Return( False)
    
    @tornado.gen.coroutine
    def Handle_signUp(self,**kwargs):

        checkcode =  kwargs.pop('checkcode')
        
        if not checkcode:
            raise tornado.gen.Return( self.on_response(kwargs,msg='Not checkcode',code=0))
        
        phone =  kwargs.get('phone',None)
        if not phone:
            raise tornado.gen.Return( self.on_response(kwargs,msg='Not phone',code=0))
        
        if self.verify_code(checkcode,phone):
            
            verify_name='verify_%s' % str(phone)
            res = yield tornado.gen.Task(self.redis_cache.delete, verify_name)
            if res:
                key_name='signup_%s' % str(phone)
                #kwargs=json.dumps(kwargs)
                res = yield tornado.gen.Task(self.redis_cache.set, key_name,json.dumps(kwargs),3600*24*30)
                #self.cache.set(key_name,kwargs,3600*24*30)
                if res:
                    mail_subject = u'体验师提交简历通知-%s-%s'
                    #mail_content = u'见标题'
                    kwargs.update({'link': 'http://xiaorizi.me'})
                    yield email_queue.sendmail_from_template(
                                subject=mail_subject,
                                from_addr=smtp_user,
                                to_addrs=recipient_addrs,
                                template_path='/data/web/web_test/life_site/dimon/templates/resume_email.html',
                                params=kwargs,
                                mime_type='html',
                                charset='utf-8',
                                scheduled_hours_from_now=0)
                    
                    raise tornado.gen.Return( self.on_response(kwargs,msg='Request is successful',code=1))

        raise tornado.gen.Return( self.on_response(kwargs,msg='Request is fail',code=0))
    
    @tornado.gen.coroutine
    def post_function(self,post_data,func=''):
        
        _code = 1
        _msg='Request is successful'
        _Handle = getattr(self, 'Handle_%s' % func, None)
        if _Handle:
            
            post_data  = yield  _Handle(**post_data)
            #return self.on_response(user_dict,msg=_msg,code=_code)
        #else:
        raise tornado.gen.Return(post_data)
        
    
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
        
        
