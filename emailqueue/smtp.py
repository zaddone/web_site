# -*- coding: utf8 -*-
"""
Copyright (c) Ralph Möritz 2014.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import absolute_import, division, print_function, with_statement

__all__ = ['TornadoSMTP']

import functools
from concurrent.futures import ThreadPoolExecutor
from socket import _GLOBAL_DEFAULT_TIMEOUT
from smtplib import SMTP, SMTP_SSL
from tornado import gen


class TornadoSMTP:

    def initialized_async(func):
        @functools.wraps(func)
        @gen.coroutine
        def wrapper(self, *args, **kwargs):
            if self._busy:
                self._smtp = yield self._busy
                self._busy = None

            result = yield func(self, *args, **kwargs)
            raise gen.Return(result)

        return wrapper

    def __init__(self, host='', port=587, user='', password='', local_hostname=None,
                 timeout=_GLOBAL_DEFAULT_TIMEOUT, use_ssl=False, keyfile=None, certfile=None):
        self._smtp = None
        self._smtp_user = user
        self._smtp_password = password
        self._pool = ThreadPoolExecutor(1)
        self._busy = self._pool.submit(self._initialize, host, port, local_hostname,
                                       timeout, use_ssl, keyfile, certfile)

    def _initialize(self, host='', port=587, local_hostname=None, timeout=_GLOBAL_DEFAULT_TIMEOUT,
                    use_ssl=False, keyfile=None, certfile=None):
        return (SMTP_SSL(host, port, local_hostname, keyfile, certfile, timeout)
                if use_ssl else SMTP(host, port, local_hostname, timeout))

    @initialized_async
    def helo(self, name=''):
        """SMTP 'helo' command.
        Hostname to send for this command defaults to the FQDN of the local
        host.
        """
        return self._pool.submit(self._smtp.helo, name)

    @initialized_async
    def ehlo(self, name=''):
        """ SMTP 'ehlo' command.
        Hostname to send for this command defaults to the FQDN of the local
        host.
        """
        return self._pool.submit(self._smtp.ehlo, name)

    @initialized_async
    def login(self):

        """Log in on an SMTP server that requires authentication.

        The arguments are:
            - user:     The user name to authenticate with.
            - password: The password for the authentication.

        If there has been no previous EHLO or HELO command this session, this
        method tries ESMTP EHLO first.

        This method will return normally if the authentication was successful.

        This method may raise the following exceptions:

         SMTPHeloError            The server didn't reply properly to
                                  the helo greeting.
         SMTPAuthenticationError  The server didn't accept the username/
                                  password combination.
         SMTPException            No suitable authentication method was
                                  found.
        """
        return self._pool.submit(self._smtp.login, self._smtp_user, self._smtp_password)

    @initialized_async
    def starttls(self, keyfile=None, certfile=None):

        """Puts the connection to the SMTP server into TLS mode.

        If there has been no previous EHLO or HELO command this session, this
        method tries ESMTP EHLO first.

        If the server supports TLS, this will encrypt the rest of the SMTP
        session. If you provide the keyfile and certfile parameters,
        the identity of the SMTP server and client can be checked. This,
        however, depends on whether the socket module really checks the
        certificates.

        This method may raise the following exceptions:

         SMTPHeloError            The server didn't reply properly to
                                  the helo greeting.
        """
        return self._pool.submit(self._smtp.starttls, keyfile, certfile)

    @initialized_async
    def sendmail(self, from_addr, to_addrs, msg, mail_options=(), rcpt_options=()):

        """This command performs an entire mail transaction.

        The arguments are:
            - from_addr    : The address sending this mail.
            - to_addrs     : A list of addresses to send this mail to.  A bare
                             string will be treated as a list with 1 address.
            - msg          : The message to send.
            - mail_options : List of ESMTP options (such as 8bitmime) for the
                             mail command.
            - rcpt_options : List of ESMTP options (such as DSN commands) for
                             all the rcpt commands.

        This method may raise the following exceptions:

         SMTPHeloError          The server didn't reply properly to
                                the helo greeting.
         SMTPRecipientsRefused  The server rejected ALL recipients
                                (no mail was sent).
         SMTPSenderRefused      The server didn't accept the from_addr.
         SMTPDataError          The server replied with an unexpected
                                error code (other than a refusal of
                                a recipient).

        Note: the connection will be open even after an exception is raised.
        """

        return self._pool.submit(self._smtp.sendmail, from_addr, to_addrs, msg, mail_options, rcpt_options)

    @initialized_async
    def quit(self):
        """Terminate the SMTP session."""
        return self._pool.submit(self._smtp.quit)
