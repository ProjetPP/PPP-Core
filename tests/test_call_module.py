"""Test the core's capabilities to calling a third-party module."""

import json
from httmock import urlmatch, HTTMock, with_httmock, all_requests

from ppp_datamodel import Missing
from ppp_datamodel.communication import Request, TraceItem, Response
from ppp_core.tests import PPPTestCase
from ppp_core import app

one_module_config = """
{
    "debug": true,
    "modules": [
        {
            "name": "my_module",
            "url": "http://test/my_module/",
            "coefficient": 1
        }
    ]
}"""

three_modules_config = """
{
    "debug": true,
    "modules": [
        {
            "name": "my_module",
            "url": "http://test/my_module/",
            "coefficient": 1
        },
        {
            "name": "my_module2",
            "url": "http://test/my_module2/",
            "coefficient": 1
        },
        {
            "name": "my_module3",
            "url": "http://test/my_module3/",
            "coefficient": 1
        }
    ]
}"""

one_valid_module_config = """
{
    "debug": true,
    "modules": [
        {
            "name": "my_module",
            "url": "http://test/my_module/",
            "coefficient": 1
        },
        {
            "name": "my_module4",
            "url": "http://test/my_module4/",
            "coefficient": 1
        }
    ]
}"""

@urlmatch(netloc='test', path='/my_module/')
def my_module_mock(url, request):
    c = '"measures": {"relevance": 0.5, "accuracy": 0.5}, "tree": {"type": "missing"}'
    return {'status_code': 200,
            'content': '[{"language": "en", %s, '
                         '"trace": [{"module": "module1", %s}]}]' %
                         (c, c)}

@urlmatch(netloc='test', path='/my_module2/')
def my_module2_mock(url, request):
    body = Request.from_json(request.body)
    m = {'relevance': 0.3, 'accuracy': 1}
    response = Response('en', body.tree, m,
                        [TraceItem('module2', body.tree, m)])
    return {'status_code': 200,
            'content': '[%s]' % response.as_json()}

@urlmatch(netloc='test', path='/my_module3/')
def my_module3_mock(url, request):
    c = '"measures": {"relevance": 0.55, "accuracy": 0.5}, "tree": {"type": "missing"}'
    return {'status_code': 200,
            'content': '[{"language": "en", %s, '
                         '"trace": [{"module": "module3", %s}]}]' % (c, c)}

@urlmatch(netloc='test', path='/my_module4/')
def my_module4_mock(url, request):
    c = '"measures": {"relevance": 0.5, "accuracy": 1.5}, "tree": {"type": "missing"}'
    return {'status_code': 200,
            'content': '[{"language": "en", %s, '
                         '"trace": [{"module": "module4", %s}]}]' % (c, c)}

class CallModuleTest(PPPTestCase(app)):
    def testQueriesModule(self):
        self.config_file.write(one_module_config)
        self.config_file.seek(0)
        q = {'id': '1', 'language': 'en', 'tree': {'type': 'triple',
             'subject': {'type': 'resource', 'value': 'foo'},
             'predicate': {'type': 'resource', 'value': 'bar'},
             'object': {'type': 'resource', 'value': 'baz'}},
             'measures': {}, 'trace': []}
        m = {'relevance': 0.5, 'accuracy': 0.5}
        with HTTMock(my_module_mock):
            self.assertResponse(q, [
                Response('en', Missing(), m,
                         [TraceItem('module1', Missing(), m)])])
    def testQueriesMultipleModule(self):
        self.config_file.write(three_modules_config)
        self.config_file.seek(0)
        q = Request('1', 'en', Missing(), {}, [])
        m1 = {'relevance': 0.5, 'accuracy': 0.5}
        m2 = {'relevance': 0.3, 'accuracy': 1}
        m3 = {'relevance': 0.55, 'accuracy': 0.5}
        with HTTMock(my_module_mock, my_module2_mock, my_module3_mock):
            self.assertResponse(q, [
                Response('en', Missing(), m3,
                         [TraceItem('module3', Missing(), m3)]),
                Response('en', Missing(), m1,
                         [TraceItem('module1', Missing(), m1)]),
                Response('en', Missing(), m2,
                         [TraceItem('module2', Missing(), m2)]),
                ])
    def testQueriesMultipleModuleWithFail(self):
        self.config_file.write(one_valid_module_config)
        self.config_file.seek(0)
        q = Request('1', 'en', Missing(), {}, [])
        m = {'relevance': 0.5, 'accuracy': 0.5}
        with HTTMock(my_module_mock, my_module4_mock):
            self.assertResponse(q, [
                Response('en', Missing(), m,
                         [TraceItem('module1', Missing(), m)])])
