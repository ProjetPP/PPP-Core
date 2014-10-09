"""Test framework for running tests of the PPP core."""

from ppp_core import app
from webtest import TestApp
from unittest import TestCase

class PPPTestCase(TestCase):
    def setUp(self):
        super(PPPTestCase, self).setUp()
        self.app = TestApp(app)
    def request(self, obj):
        return self.app.post_json('/', obj).json
    def assertResponse(self, request, response):
        self.assertEqual(self.request(request), response)
    def assertStatusInt(self, request, status):
        self.assertEqual(self.app.post_json(request, status='*').status_int, status)

