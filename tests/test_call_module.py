"""Test the core's capabilities to calling a third-party module."""

import json
from httmock import urlmatch, HTTMock, with_httmock, all_requests

from ppp_core.tests import PPPTestCase

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
    return {'status_code': 200,
            'content': '{"language": "en", "pertinence": 0.5, "tree": {}}'}

@urlmatch(netloc='test', path='/my_module2/')
def my_module2_mock(url, request):
    body = json.loads(request.body)
    body['pertinence'] = 1
    return {'status_code': 200,
            'content': json.dumps(body)}

@urlmatch(netloc='test', path='/my_module3/')
def my_module3_mock(url, request):
    return {'status_code': 200,
            'content': '{"language": "en", "pertinence": 0.5, "tree": {}}'}

@urlmatch(netloc='test', path='/my_module4/')
def my_module4_mock(url, request):
    return {'status_code': 200,
            'content': '{"language": "en", "pertinence": 1.5, '
                       '"tree": {"type": "missing"}}'}

class CallModuleTest(PPPTestCase):
    def testQueriesModule(self):
        self.config_file.write(one_module_config)
        self.config_file.seek(0)
        q = {'language': 'en', 'tree': {'type': 'triple',
             'subject': {'type': 'resource', 'value': 'foo'},
             'predicate': {'type': 'resource', 'value': 'bar'},
             'object': {'type': 'resource', 'value': 'baz'},
            }}
        with HTTMock(my_module_mock):
            self.assertResponse(q, {'language': 'en', 'pertinence': 0.5, 'tree': {}})
    def testQueriesMultipleModule(self):
        self.config_file.write(three_modules_config)
        self.config_file.seek(0)
        q = {'language': 'en', 'tree': {'type': 'missing'}}
        with HTTMock(my_module_mock, my_module2_mock, my_module3_mock):
            self.assertResponse(q, {'language': 'en', 'pertinence': 1,
                                    'tree': {'type': 'missing'}})
    def testQueriesMultipleModule(self):
        self.config_file.write(one_valid_module_config)
        self.config_file.seek(0)
        q = {'language': 'en', 'tree': {'type': 'missing'}}
        with HTTMock(my_module_mock, my_module4_mock):
            self.assertResponse(q, {'language': 'en', 'pertinence': 0.5,
                                    'tree': {}})
