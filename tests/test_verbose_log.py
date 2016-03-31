"""Test verbose logging."""

import os
import json
import time
import sqlite3
import tempfile

from httmock import urlmatch, HTTMock, with_httmock, all_requests

from ppp_datamodel.communication import Request, TraceItem, Response
from ppp_datamodel import Resource, Missing
from ppp_libmodule.tests import PPPTestCase

from ppp_core import app

config1 = """
{
    "debug": true,
    "modules": [
        {
            "name": "my_module",
            "url": "http://test/my_module/",
            "coefficient": 1
        }
    ],
    "log": {
        "verbose_database_url": "sqlite:///%s"
    }
}"""

@urlmatch(netloc='test', path='/my_module/')
def my_module_mock(url, request):
    r = Request.from_json(request.body)
    if r.tree == Resource('one'):
        c = '"measures": {"accuracy": 1, "relevance": 1}, "tree": {"type": "resource", "value": "two"}'
        return {'status_code': 200,
                'content': '[{"language": "en", %s, '
                             '"trace": [{"module": "module1", %s}]}]' %
                             (c, c)}
    else:
        return {'status_code': 200,
                'content': '[]'}

class TestVerboseLog(PPPTestCase(app)):
    config_var = 'PPP_CORE_CONFIG'

    def setUp(self):
        self.fd = tempfile.NamedTemporaryFile('w+')
        self.config = config1 % self.fd.name
        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.fd.close()

    def testVerboseLog(self):
        q = Request('1', 'en', Resource('one'), {}, [])
        with HTTMock(my_module_mock):
            answers = self.request(q)

        time.sleep(0.1)

        conn = sqlite3.connect(self.fd.name)
        with conn:
            r = conn.execute('SELECT request_handling_start_time, request_handling_end_time, request_answers_json FROM requests;').fetchall()
            fields = ('start', 'end', 'answers')
            zipper = lambda x:{'start': x[0], 'end': x[1],
                               'answers': json.loads(x[2])}
            r = list(map(zipper, r))

        self.assertEqual(len(r), 1, r)
        self.assertAlmostEqual(r[0]['start'], time.time(), delta=1.)
        self.assertAlmostEqual(r[0]['end'], time.time(), delta=1.)
        self.assertEqual(len(r[0]['answers']), 1, r[0]['answers'])
        self.assertEqual(set(r[0]['answers'][0]), {'language', 'tree', 'measures', 'trace'})
