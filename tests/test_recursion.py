import json
from httmock import urlmatch, HTTMock, with_httmock, all_requests

from ppp_datamodel import Resource, Missing
from ppp_datamodel.communication import Request, TraceItem, Response
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
            "name": "my_module3",
            "url": "http://test/my_module3/",
            "coefficient": 1
        },
        {
            "name": "my_module3b",
            "url": "http://test/my_module3b/",
            "coefficient": 1
        }
    ]
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

@urlmatch(netloc='test', path='/my_module2/')
def my_module2_mock(url, request):
    r = Request.from_json(request.body)
    if r.tree == Resource('two'):
        c = '"measures": {"accuracy": 1, "relevance": 2}, "tree": {"type": "resource", "value": "three"}'
        return {'status_code': 200,
                'content': '[{"language": "en", %s, '
                             '"trace": [{"module": "module1", %s}]}]' %
                             (c, c)}
    else:
        return {'status_code': 200,
                'content': '[]'}

@urlmatch(netloc='test', path='/my_module3/')
def my_module3_mock(url, request):
    c = '"measures": {"accuracy": 1, "relevance": 1}, "tree": {"type": "resource", "value": "two"}'
    return {'status_code': 200,
            'content': '[{"language": "en", %s, '
                         '"trace": [{"module": "module3", %s}]}]' %
                         (c, c)}

@urlmatch(netloc='test', path='/my_module3b/')
def my_module3b_mock(url, request):
    c = '"measures": {"accuracy": 1, "relevance": 1}, "tree": {"type": "resource", "value": "two"}'
    return {'status_code': 200,
            'content': '[{"language": "en", %s, '
                         '"trace": [{"module": "module3", %s}]}]' %
                         (c, c)}


class TestRecursion1(PPPTestCase(app)):
    config_var = 'PPP_CORE_CONFIG'
    config = config1
    def testRecursion(self):
        q = Request('1', 'en', Resource('one'), {}, [])
        with HTTMock(my_module_mock, my_module2_mock, my_module3_mock):
            answers = self.request(q)
            self.assertEqual(len(answers), 2, answers)
            self.assertEqual(answers[0].tree, Resource('three'))
            self.assertEqual(answers[1].tree, Resource('two'))

class TestRecursion2(PPPTestCase(app)):
    config_var = 'PPP_CORE_CONFIG'
    config = config2
    def testNoDuplicate(self):
        q = Request('1', 'en', Missing(), {}, [])
        with HTTMock(my_module3_mock, my_module3b_mock):
            answers = self.request(q)
            self.assertNotEqual(len(answers), 20, answers)
            self.assertNotEqual(len(answers), 10, answers)
            self.assertNotEqual(len(answers), 2, answers)
            self.assertEqual(len(answers), 1, answers)
