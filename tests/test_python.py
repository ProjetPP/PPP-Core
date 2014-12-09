import json
from httmock import urlmatch, HTTMock, with_httmock, all_requests

from ppp_datamodel import Resource, Missing, Sentence
from ppp_datamodel.communication import Request, TraceItem, Response
from ppp_libmodule.tests import PPPTestCase
from ppp_core import app, router


config1 = """
{
    "debug": true,
    "modules": [
        {
            "name": "my_module1",
            "url": "http://test/my_module1/",
            "coefficient": 1
        },
        {
            "name": "my_module2",
            "url": "python:tests.test_python:Module2",
            "coefficient": 1
        },
        {
            "name": "my_module3",
            "url": "python:tests.test_python:Module3",
            "coefficient": 1
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
class Module2:
    def __init__(self, request):
        self.request = request

    def answer(self):
        return [Response(1, self.request.tree, {}, [])]

class Module3:
    def __init__(self, request):
        self.request = request

    def answer(self):
        assert False


class FakeLogger:
    def __init__(self):
        self._errors = []
    def error(self, s):
        self._errors.append(s)
    def info(self, s):
        pass

class TestPython(PPPTestCase(app)):
    config_var = 'PPP_CORE_CONFIG'
    config = config1
    def testPython(self):
        with HTTMock(my_module1_mock):
            q = Request('1', 'en', Sentence('foo'), {}, [])
            (router.logger, logger) = (FakeLogger(), router.logger)
            try:
                answers = self.request(q)
            finally:
                (fakelogger, router.logger) = (router.logger, logger)
            self.assertEqual(len(answers), 3, answers)
            self.assertEqual(len(list(filter(lambda x:x.tree.value == 'foo', answers))), 1)
            self.assertEqual(len(list(filter(lambda x:x.tree.value == 'one', answers))), 2)
            self.assertEqual(len(fakelogger._errors), 4, fakelogger._errors)
