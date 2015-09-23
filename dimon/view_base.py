#coding:utf-8
__author__ = 'zaddone'
import json
import re
import hashlib
import tornado.web
import tornado.httpclient
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr


#import tornado.template as template





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
        json = self.get_argument('json',None)
        if json:
            self.write(self.on_response(_data))
        else:
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

    def get_json_info(self,json_str):
        return eval(json_str.encode('utf-8'), type('Dummy', (dict,), dict(__getitem__=lambda s,n:n))())
    @tornado.gen.coroutine
    def get_db_city(self,usetype=1):

        sql='SELECT `district_id`,`district_name`,`title` FROM `sys_new_district` WHERE `usetype`= %d' % usetype

        return self.db.query(sql)

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
            if int(res.body) > 0:
                raise tornado.gen.Return(True)
                #return True
            else:
                raise tornado.gen.Return(False)
                #return res
                #return False
            
        else:
            raise tornado.gen.Return(False)
            #return  False
    @tornado.gen.coroutine
    def send_mail(self,subject, content, mail_to, mail_host, mail_user, mail_pass, 
                      content_html=None, mail_user_header=None, img_patch=[], cc_list=[]):
    
        if not all((subject, content, mail_to, mail_host, mail_user, mail_pass)):
            return False
        
        
        msg = MIMEMultipart('alternative')
        msg["Accept-Language"]="zh-CN"
        msg["Accept-Charset"]="ISO-8859-1,utf-8"
        msg['Subject'] = subject
        msg['Cc'] = ';'.join(cc_list)
        
        if isinstance(mail_to, (tuple, list)):
            msg['to'] = ';'.join(mail_to)
        else:
            msg['to'] = mail_to
        
        part1 = MIMEText(content, 'plain', 'utf-8')
        msg.attach(part1)
        
        if content_html:
            part2 = MIMEText(content_html, 'html', 'utf-8')
            msg.attach(part2)
        
        if img_patch and not isinstance(img_patch, (list, tuple)):
            img_patch = [img_patch]
        
        for img in img_patch:
            fp = open(img['fn'], 'rb')                                                    
            part3 = MIMEImage(fp.read())
            fp.close()
            part3.add_header('Content-ID', img['cid'])
            msg.attach(part3)
        
        if mail_user_header:
            mail_user_header = formataddr((str(Header(mail_user_header, 'utf-8')), mail_user))
            msg['From'] = mail_user_header
        else:
            msg['From'] = mail_user
        
        try:
            s = smtplib.SMTP()
            #connect = yield tornado.gen.Task(s.connect, mail_host)
            s.connect(mail_host)
            #s.esmtp_features["auth"]="LOGIN PLAIN"
            #login = yield tornado.gen.Task(s.login, mail_user, mail_pass)
            #sendmail=yield tornado.gen.Task(s.sendmail, mail_user, mail_to, msg.as_string())
            s.login(mail_user, mail_pass)
            #log.debug('successful login')
            #s.sendmail(mail_user, to_list.extend(bcc_list), msg.as_string())
            s.sendmail(mail_user, mail_to, msg.as_string())
            #if connect and login and sendmail:
                #sendmail=yield tornado.gen.Task(s.sendmail, mail_user, mail_to, msg.as_string())
            raise tornado.gen.Return(True)
            #s.sendmail(mail_user, mail_to, msg.as_string())
            #yield True
        except Exception, e:
            #log.debug('Email Error: %s' %e)
            pass
        raise tornado.gen.Return(False)
    '''
    def SendEmailMsg(self,e_model):
        mail_host = 'smtp.exmail.qq.com'
        mail_user = 'zl.feng@xiaorizi.me'
        mail_pass = '520512fzl520512'
        
        mail_subject = u'体验师提交简历通知-%s-%s' %(e_model.name, e_model.nickname)
        mail_content = u'见标题'
        
        html_template = get_template('explorer_resume/resume_email.html')
        try:
            writing = 'http://api.xiaorizi.me%s' %e_model.writing.url
        except:
            writing=''
            
        try:
            urlss='http://api.xiaorizi.me%s' %e_model.files.url
        except:
            urlss=''
        
        d = Context({
            'realname': c_model.realname,
            'nickname': c_model.name,
            'head_url': 'http://api.xiaorizi.me%s' %e_model.head.url if e_model.head else '',
            'sex': c_model.get_sex_display(),
            'birthday': c_model.birthday.strftime('%Y-%m-%d'),
            'profession': c_model.profession_detail if c_model.profession == 2 \
                    and c_model.profession_detail \
                    else c_model.get_profession_display(),
            'phone': c_model.phone,
            'wechat': c_model.wechat,
            'email': c_model.email,
            'hobby': c_model.hobby,
            'residence': e_model.residence,
            'ex_cities': ','.join([ct.district_name for ct in e_model.city.all()]),
            'remark': e_model.remark,
            'submission': e_model.submission,
            'info_from': e_model.info_from,
            'writing_url': writing,
            'files_url':urlss ,
            })
        
        html_content = html_template.render(d)
        
        mail_to = ('252925359@qq.com','516139718@qq.com', 'xy.huang@xiaorizi.me', '9682539@qq.com')
        #mail_to = ('252925359@qq.com', )
        send_mail_api(mail_subject, mail_content, mail_to, mail_host, mail_user, mail_pass,
                content_html=html_content)
        '''