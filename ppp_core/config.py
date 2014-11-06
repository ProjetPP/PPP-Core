"""Configuration module."""

import os
import json
import logging
from collections import namedtuple
from .exceptions import InvalidConfig

class Module(namedtuple('_Module', 'name url coefficient')):
    """Represents a modules of the core with its name, URL, and a
    coefficient applied to it self-computed pertinence."""
    def __new__(cls, name, url, coefficient=1, **kwargs):
        if kwargs: # pragma: no cover
            logging.warning('Ignored arguments to module config: %r' % kwargs)
        return super(Module, cls).__new__(cls,
                                          name=name,
                                          url=url,
                                          coefficient=coefficient)


class Config:
    __slots__ = ('debug',)
    def __init__(self, data=None):
        if not hasattr(self, 'config_path_variable') or \
                not hasattr(self, 'parse_config'):
            raise NotImplementedError('Config class does not implement all '
                                      'required attributes.')
        self.debug = True
        if not data:
            try:
                with open(self.get_config_path()) as fd:
                    data = json.load(fd)
            except ValueError as exc:
                raise InvalidConfig(*exc.args)
        self.parse_config(data)

    @classmethod
    def get_config_path(cls):
        path = os.environ.get(cls.config_path_variable, '')
        if not path:
            raise InvalidConfig('Could not find config file, please set '
                                'environment variable $%s.' %
                                cls.config_path_variable)
        return path
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

