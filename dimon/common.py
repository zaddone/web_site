import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr

def send_mail(subject, content, mail_to, mail_host, mail_user, mail_pass, 
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
        s.connect(mail_host)
        #s.esmtp_features["auth"]="LOGIN PLAIN"
        s.login(mail_user, mail_pass)
        #log.debug('successful login')
        #s.sendmail(mail_user, to_list.extend(bcc_list), msg.as_string())
    
        s.sendmail(mail_user, mail_to, msg.as_string())
        return True
    except Exception, e:
        #log.debug('Email Error: %s' %e)
        return False