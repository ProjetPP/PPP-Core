"""Configuration module."""

import os
import json
import logging
from collections import namedtuple
from ppp_libmodule.config import Config
from ppp_libmodule.exceptions import InvalidConfig

class Module(namedtuple('_Module', 'name url coefficient filters method')):
    """Represents a modules of the core with its name, URL, and a
    coefficient applied to it self-computed pertinence."""
    def __new__(cls, name, url, coefficient=1, filters=None, **kwargs):
        if kwargs: # pragma: no cover
            logging.warning('Ignored arguments to module config: %r' % kwargs)
        if url.startswith('python:'):
            url = url[len('python:'):]
            method = 'python'
        else:
            method = 'http'
        return super(Module, cls).__new__(cls,
                                          name=name,
                                          url=url,
                                          method=method,
                                          coefficient=coefficient,
                                          filters=filters or {})

    def should_send(self, request):
        """Returns whether or not the request should be sent to the
        modules, based on the filters."""
        if self.filters.get('whitelist', None):
            return request.tree.type in self.filters['whitelist']
        elif self.filters.get('blacklist', None):
            return request.tree.type not in self.filters['blacklist']
        else:
            return True


class CoreConfig(Config):
    __slots__ = ('modules', 'nb_passes')
    config_path_variable = 'PPP_CORE_CONFIG'

    def parse_config(self, data):
        self.modules = self._parse_modules(data.get('modules', {}))
        self.debug = data.get('debug', False)
        self.nb_passes = data.get('recursion', {}).get('max_passes', 10)

    def _parse_modules(self, data):
        modules = []
        for config in data:
            if 'name' not in config:
                raise InvalidConfig('Module %r has no name' % config)
            if 'url' not in config:
                raise InvalidConfig('Module %s has no set URL.' %
                        config['name'])
            modules.append(Module(**config))
        return modules

