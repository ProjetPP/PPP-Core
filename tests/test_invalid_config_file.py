"""Tests what happens if the config file is invalid."""

import os
import tempfile
from ppp_core import app
from webtest import TestApp
from unittest import TestCase
from ppp_core.exceptions import InvalidConfig

class InvalidConfFileTestCase(TestCase):
    def testNoConfFile(self):
        self.app = TestApp(app)
        obj = {'language': 'en', 'tree': {}}
        self.assertRaises(InvalidConfig, self.app.post_json,
                          '/', obj, status='*')

    def testEmptyConfFile(self):
        self.app = TestApp(app)
        self.config_file = tempfile.NamedTemporaryFile('w+')
        os.environ['PPP_CORE_CONFIG'] = self.config_file.name
        obj = {'language': 'en', 'tree': {}}
        self.assertRaises(InvalidConfig, self.app.post_json,
                          '/', obj, status='*')
        del os.environ['PPP_CORE_CONFIG']
        del self.config_file

    def testModuleWithNoName(self):
        self.app = TestApp(app)
        self.config_file = tempfile.NamedTemporaryFile('w+')
        self.config_file.write('''{"debug": true, "modules": [{
            "url": "http://foo/bar/"}]}''')
        self.config_file.seek(0)
        os.environ['PPP_CORE_CONFIG'] = self.config_file.name
        obj = {'language': 'en', 'tree': {}}
        self.assertRaises(InvalidConfig, self.app.post_json,
                          '/', obj, status='*')
        del os.environ['PPP_CORE_CONFIG']
        del self.config_file

    def testModuleWithNoUrl(self):
        self.app = TestApp(app)
        self.config_file = tempfile.NamedTemporaryFile('w+')
        self.config_file.write('''{"debug": true, "modules": [{
            "name": "foo"}]}''')
        self.config_file.seek(0)
        os.environ['PPP_CORE_CONFIG'] = self.config_file.name
        obj = {'language': 'en', 'tree': {}}
        self.assertRaises(InvalidConfig, self.app.post_json,
                          '/', obj, status='*')
        del os.environ['PPP_CORE_CONFIG']
        del self.config_file
