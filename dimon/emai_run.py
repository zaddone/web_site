import sys
from tornado import httpserver, ioloop, web
from emailqueue.queues import MongoDbEmailQueue
from tornado.options import define, options
#c = tornadoredis.Client()
#mail_to = ('252925359@qq.com', )
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

define("port", default=8888, help="run on the given port", type=int)
class MainHandler(web.RequestHandler):

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


def main(port):
    options.parse_command_line()
    application = web.Application([
        (r"/", MainHandler),
    ])

    # Add email queue callback to IOLoop
    ioloop.IOLoop.current().add_callback(email_queue.worker)

    http_server = httpserver.HTTPServer(application)
    http_server.listen(port)
    ioloop.IOLoop.current().start()


if __name__ == "__main__":
    try:
        main(int(sys.argv[1]))
    except:
        main(options.port)
    
    
