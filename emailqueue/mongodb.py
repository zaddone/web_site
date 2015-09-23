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

__all__ = ['MongoDbService']

from tornado import gen
import motor
import datetime
import json
import bson.objectid


def json_default(obj):
    """Default JSON serializer."""
    if isinstance(obj, bson.objectid.ObjectId):
        return str(obj)
    elif isinstance(obj, datetime.datetime):
        return obj.strftime("%Y-%m-%d %H:%M")
    else:
        raise TypeError("%s is not JSON-serializable" % repr(obj))


def json_loads(data):
    return json.loads(data)


def json_dumps(instance):
    return json.dumps(instance, default=json_default)


class MongoDbService(object):

    def __init__(self, uri_connection, database):
        client = motor.MotorClient(uri_connection)
        self.db = client[database]

    @gen.coroutine
    def insert(self, collection, document):
        result = yield self.db[collection].insert(document)
        json_data = json_dumps(result)
        raise gen.Return(json_data)

    @gen.coroutine
    def update(self, collection, _id, document):
        result = yield self.db[collection].update({'_id': _id}, {'$set': document})
        json_data = json_dumps(result)
        raise gen.Return(json_data)

    @gen.coroutine
    def find(self, collection, query=None, skip=0, limit=1000):

        if query:
            cursor = self.db[collection]\
                .find(query)\
                .limit(limit)\
                .skip(skip)
        else:
            cursor = self.db[collection]\
                .find()\
                .limit(limit)\
                .skip(skip)

        result = yield cursor.to_list(length=limit)

        raise gen.Return(result)
