"""Test framework for running tests of the PPP core."""

__all__ = ['PPPTestCase']

import os
import tempfile
from ppp_core import app
from webtest import TestApp
from unittest import TestCase

base_config = """
{
    "debug": true,
    "modules": []
}
"""

class PPPTestCase(TestCase):
    def setUp(self):
        super(PPPTestCase, self).setUp()
        self.app = TestApp(app)
        self.config_file = tempfile.NamedTemporaryFile('w+')
        os.environ['PPP_CORE_CONFIG'] = self.config_file.name
        self.config_file.write(base_config)
        self.config_file.seek(0)
    def tearDown(self):
        self.config_file.close()
        del os.environ['PPP_CORE_CONFIG']
        del self.config_file
        super(PPPTestCase, self).tearDown()

    def request(self, obj):
        return self.app.post_json('/', obj).json
    def assertResponse(self, request, response):
        self.assertEqual(self.request(request), response)
    def assertStatusInt(self, request, status):
        res = self.app.post_json('/', request, status='*')
        self.assertEqual(res.status_int, status)

