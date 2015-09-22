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

class mongotest(baseHandler):
    def get(self):

        # Put new email in the queue for processing
        # by the mailer worker at the scheduled time.
        email_queue.sendmail(
            subject='Hello World Sample',
            from_addr=smtp_user,
            to_addrs=recipient_addrs,
            text='Greetings from Tornado Email Queue.',
            mime_type='plain',
            charset='utf-8',
            scheduled_hours_from_now=0
        )

        # Render a tornado html template and put it in the queue
        # for processing by the mailer worker at the scheduled time.
        email_queue.sendmail_from_template(
            subject='Tornado Templates Sample',
            from_addr=smtp_user,
            to_addrs=recipient_addrs,
            template_path='templates/email.html',
            params={'link': 'http://ricardoyorky.github.io/emailqueue/'},
            mime_type='html',
            charset='utf-8',
            scheduled_hours_from_now=0
        )

        self.write("Mail sent")
    

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
            self.return_style(template='sign_in.html',_data=[])
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
        
        k =yield self.post_function(post_data,func=post_data.pop('func'))

        self.write(k)

    

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

        #key_val={}
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
                    
                    raise tornado.gen.Return( self.on_response(kwargs,msg='Request is successful,Email err',code=1))
        

        mail_host = 'smtp.exmail.qq.com'
        mail_user = 'zl.feng@xiaorizi.me'
        mail_pass = '520512fzl520512'

        #mail_subject = u'体验师提交简历通知-%s-%s' %(e_model.name, e_model.nickname)
        mail_subject = u'体验师提交简历通知-%s-%s'
        mail_content = u'见标题'
        mail_to = ('252925359@qq.com', )
        #email_send = self.send_mail(mail_subject, mail_content, mail_to, mail_host, mail_user, mail_pass)
        
        sendM =yield email_queue.sendmail(
                    subject=mail_subject,
                    from_addr=smtp_user,
                    to_addrs=recipient_addrs,
                    text=mail_content,
                    mime_type='plain',
                    charset='utf-8',
                    scheduled_hours_from_now=0
                )
        '''
        sendM = yield tornado.gen.Task(email_queue.sendmail,subject=mail_subject,
                    from_addr=smtp_user,
                    to_addrs=mail_to,
                    text=mail_content,
                    mime_type='plain',
                    charset='utf-8',
                    scheduled_hours_from_now=0)
        '''
        #if sendM:
        #if email_send:
        raise tornado.gen.Return( self.on_response(kwargs,msg='Email request is successful %s' % sendM,code=1))
        
        
        raise tornado.gen.Return( self.on_response(kwargs,msg='Request is fail',code=0))
    
    
    '''
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
    '''
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
        
        
