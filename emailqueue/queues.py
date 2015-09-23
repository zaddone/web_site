"""
The MIT License (MIT)

Copyright (c) 2015 Ricardo Yorky

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from __future__ import absolute_import, division, print_function, with_statement

__all__ = ['MongoDbEmailQueue']

from tornado import queues, gen, template
from emailqueue import mongodb, smtp
from email.mime.text import MIMEText
from email.utils import make_msgid, formatdate
import datetime


class MongoDbEmailQueue(object):

    def __init__(self, smtp_host, smtp_port, smtp_user, smtp_password, mongodb_uri,
                 mongodb_database, mongodb_collection='email_queue', queue_maxsize=100):
        super(MongoDbEmailQueue, self).__init__()
        self._queue = queues.Queue(maxsize=queue_maxsize)
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._smtp_user = smtp_user
        self._smtp_password = smtp_password
        self._mongodb = mongodb.MongoDbService(uri_connection=mongodb_uri, database=mongodb_database)
        self._mongodb_collection = mongodb_collection
        self._template_loader = template.Loader('.')

    @gen.coroutine
    def __load_work(self):

        query = {
            "status": "Pending",
            "scheduled_date": {"$lte": datetime.datetime.now()}
        }

        email_list = yield self._mongodb.find(collection=self._mongodb_collection, query=query)

        for email in email_list:
            yield self._queue.put(email)

    @gen.coroutine
    def worker(self):

        while True:

            if self._queue.empty():
                yield gen.sleep(0.5)
                yield self.__load_work()

            else:
                item = yield self._queue.get()
                scheduled_date = item['scheduled_date']
                now = datetime.datetime.now()

                if scheduled_date <= now:

                    _smtp = None

                    try:
                        _smtp = smtp.TornadoSMTP(host=self._smtp_host, port=self._smtp_port,
                                                 user=self._smtp_user, password=self._smtp_password)
                        yield _smtp.ehlo()
                        yield _smtp.starttls()
                        yield _smtp.login()
                        item['to'] = ','.join( item['to'] )
                        msg = MIMEText(item['text'], item['mime_type'], item['charset'])
                        msg['Subject'] = item['subject']
                        msg['From'] = item['from']
                        msg['To'] = item['to']
                        msg['Date'] = formatdate()
                        msg['Reply-To'] = item['from']
                        msg['Message-Id'] = make_msgid(str(item['_id']))
                        
                        yield _smtp.sendmail(from_addr=item['from'], to_addrs=item['to'], msg=msg.as_string())

                        update_document = {
                            'status': 'Sent',
                            'sent_date': now
                        }

                        yield self._mongodb.update(collection=self._mongodb_collection,
                                                   _id=item['_id'], document=update_document)

                    finally:
                        self._queue.task_done()

                        if _smtp:
                            yield _smtp.quit()

    @gen.coroutine
    def sendmail(self, subject, from_addr, to_addrs, text, mime_type='plain',
                 charset='utf-8', scheduled_hours_from_now=0):

        """Put new mail in the queue for processing by the worker at the scheduled time.

        The arguments are:
            - subject                   : The subject of the mail.
            - from_addr                 : The address sending this mail.
            - to_addrs                  : A list of addresses to send this mail to.
                                          A bare string will be treated as a list with 1 address.
            - text                      : Is the string for the message object.
            - mime_type                 : Is the MIME sub content type, defaulting to "plain".
            - charset                   : Is the character set parameter added to the Content-Type
            - scheduled_hours_from_now  : Hours for set the scheduled date from now. 0 for now.
        """

        created_date = datetime.datetime.now()
        scheduled_date = created_date + datetime.timedelta(hours=int(scheduled_hours_from_now))

        item = {
            'subject': subject,
            'from': from_addr,
            'to': to_addrs,
            'text': text,
            'mime_type': mime_type,
            'charset': charset,
            'status': 'Pending',
            'created_date': created_date,
            'scheduled_date': scheduled_date,
            'sent_date': None
        }

        yield self._mongodb.insert(collection=self._mongodb_collection, document=item)

    @gen.coroutine
    def sendmail_from_template(self, subject, from_addr, to_addrs, template_path, params,
                               mime_type='html', charset='utf-8', scheduled_hours_from_now=0):

        """Render a tornado template and put it in the queue for processing by the worker at the scheduled time.

        The arguments are:
            - subject                   : The subject of the mail.
            - from_addr                 : The address sending this mail.
            - to_addrs                  : A list of addresses to send this mail to.
                                          A bare string will be treated as a list with 1 address.
            - template_path             : The path to the template file. 'templates/my-template.html'
            - params                    : Dictionary for passing parameters to templates. {'Name': Joe}
            - mime_type                 : Is the MIME sub content type, defaulting to "plain".
            - charset                   : Is the character set parameter added to the Content-Type
            - scheduled_hours_from_now  : Hours for set the scheduled date from now. 0 for now.
        """

        text = self._template_loader.load(template_path).generate(**params)

        yield self.sendmail(subject=subject,
                            from_addr=from_addr,
                            to_addrs=to_addrs,
                            text=text,
                            mime_type=mime_type,
                            charset=charset,
                            scheduled_hours_from_now=scheduled_hours_from_now)
