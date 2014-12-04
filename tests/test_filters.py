import json
from httmock import urlmatch, HTTMock, with_httmock, all_requests

from ppp_datamodel import Resource, Missing, Sentence
from ppp_datamodel.communication import Request, TraceItem, Response
from ppp_libmodule.tests import PPPTestCase
from ppp_core import app


config1 = """
{
    "debug": true,
    "modules": [
        {
            "name": "my_module",
            "url": "http://test/my_module1/",
            "coefficient": 1,
            "filters": {
                "whitelist": ["sentence", "triple"]
            }
        },
        {
            "name": "my_module2",
            "url": "http://test/my_module2/",
            "coefficient": 1
        }
    ]
}"""


config2 = """
{
    "debug": true,
    "modules": [
        {
            "name": "my_module",
            "url": "http://test/my_module1/",
            "coefficient": 1
        },
        {
            "name": "my_module2",
            "url": "http://test/my_module2/",
            "coefficient": 1,
            "filters": {
                "blacklist": ["triple", "missing", "resource"]
            }
        }
    ]
}"""

@urlmatch(netloc='test', path='/my_module1/')
def my_module1_mock(url, request):
    c = '"measures": {"accuracy": 1, "relevance": 1}, "tree": {"type": "resource", "value": "one"}'
    return {'status_code': 200,
            'content': '[{"language": "en", %s, '
                         '"trace": [{"module": "module1", %s}]}]' %
                         (c, c)}
@urlmatch(netloc='test', path='/my_module2/')
def my_module2_mock(url, request):
    c = '"measures": {"accuracy": 1, "relevance": 1}, "tree": {"type": "resource", "value": "two"}'
    return {'status_code': 200,
            'content': '[{"language": "en", %s, '
                         '"trace": [{"module": "module1", %s}]}]' %
                         (c, c)}


class TestWhitelist(PPPTestCase(app)):
    config_var = 'PPP_CORE_CONFIG'
    config = config1
    def testWhitelist(self):
        with HTTMock(my_module1_mock, my_module2_mock):
            q = Request('1', 'en', Sentence('foo'), {}, [])
            answers = self.request(q)
            self.assertEqual(len(answers), 2, answers)
            q = Request('1', 'en', Missing(), {}, [])
            answers = self.request(q)
            self.assertEqual(len(answers), 1, answers)
            self.assertEqual(answers[0].tree.value, 'two')


class TestBlacklist(PPPTestCase(app)):
    config_var = 'PPP_CORE_CONFIG'
    config = config2
    def testBlacklist(self):
        with HTTMock(my_module1_mock, my_module2_mock):
            q = Request('1', 'en', Sentence('foo'), {}, [])
            answers = self.request(q)
            self.assertEqual(len(answers), 2, answers)
            q = Request('1', 'en', Missing(), {}, [])
            answers = self.request(q)
            self.assertEqual(len(answers), 1, answers)
            self.assertEqual(answers[0].tree.value, 'one')
