"""Tests what happens if the config file is invalid."""

import os
import tempfile
from ppp_core import app
from webtest import TestApp
from unittest import TestCase
from ppp_core.exceptions import InvalidConfig


class NoConfFileTestCase(TestCase):
    def testNoConfFile(self):
        self.app = TestApp(app)
        obj = {'language': 'en', 'tree': {'type': 'missing'}}
        self.assertRaises(InvalidConfig, self.app.post_json,
                          '/', obj, status='*')

class InvalidConfFileTestCase(TestCase):
    def setUp(self):
        super(InvalidConfFileTestCase, self).setUp()
        self.app = TestApp(app)
        self.config_file = tempfile.NamedTemporaryFile('w+')
        os.environ['PPP_CORE_CONFIG'] = self.config_file.name
    def tearDown(self):
        del os.environ['PPP_CORE_CONFIG']
        self.config_file.close()
        del self.config_file
        super(InvalidConfFileTestCase, self).tearDown()
    def testEmptyConfFile(self):
        obj = {'language': 'en', 'tree': {'type': 'missing'}}
        self.assertRaises(InvalidConfig, self.app.post_json,
                          '/', obj, status='*')

    def testModuleWithNoName(self):
        self.config_file.write('''{"debug": true, "modules": [{
            "url": "http://foo/bar/"}]}''')
        self.config_file.seek(0)
        obj = {'language': 'en', 'tree': {'type': 'missing'}}
        self.assertRaises(InvalidConfig, self.app.post_json,
                          '/', obj, status='*')

    def testModuleWithNoUrl(self):
        self.config_file.write('''{"debug": true, "modules": [{
            "name": "foo"}]}''')
        self.config_file.seek(0)
        obj = {'language': 'en', 'tree': {'type': 'missing'}}
        self.assertRaises(InvalidConfig, self.app.post_json,
                          '/', obj, status='*')
