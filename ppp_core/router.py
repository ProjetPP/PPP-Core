"""Router of the PPP core."""

import json
import logging
import requests
import operator
import itertools
import functools
import traceback
import importlib
import ppp_libmodule
from ppp_datamodel import AbstractNode
from ppp_datamodel.communication import Request, Response, TraceItem
from .config import CoreConfig
from .exceptions import ClientError, BadGateway

s = lambda x:x if isinstance(x, str) else x.decode()

DEFAULT_ACCURACY = 0
DEFAULT_RELEVANCE = 0

try:
    level = getattr(logging, CoreConfig().loglevel.upper(), None)
except ppp_libmodule.exceptions.InvalidConfig:
    pass
else:
    if not isinstance(level, int):
        logger.error('Invalid log level: %s' % self.config.loglevel)
    else:
        logging.basicConfig(level=level)
logger = logging.getLogger('router')

def freeze(obj):
    if isinstance(obj, dict):
        return frozenset((freeze(x), freeze(y)) for (x,y) in obj.items())
    elif isinstance(obj, list):
        return tuple(map(freeze, obj))
    elif isinstance(obj, set):
        return frozenset(map(freeze, obj))
    elif isinstance(obj, TraceItem):
        return freeze(obj.as_dict())
    elif isinstance(obj, (str, tuple, frozenset, int, float)):
        return obj
    else:
        raise Exception(obj)

def answer_id(answer):
    return (answer.language, answer.tree,
            frozenset(answer.measures.items()))
def remove_duplicates(reference, new):
    result = []
    for x in new:
        id_ = answer_id(x)
        if id_ in reference:
            continue
        reference.append(id_)
        result.append(x)
    return result


class Router:
    def __init__(self, request):
        self.id = request.id
        self.language = request.language
        assert isinstance(request.tree, AbstractNode)
        self.tree = request.tree
        logger.info('Request: %s' % self.tree)
        self.measures = request.measures
        self.trace = request.trace
        self.config = CoreConfig()

    def answer(self):
        answer_ids = []
        answers = []
        new_answers = [Response(self.language, self.tree,
                                self.measures, self.trace)]
        for i in range(0, self.config.nb_passes):
            # Perform the pass
            requests = list(map(self.request_from_answer, new_answers))
            new_answers = []
            for request in requests:
                new_answers.extend(self.one_pass(request))
            # Remove duplicates, and update the answer list
            new_answers = list(remove_duplicates(answer_ids, new_answers))
            answers.extend(new_answers)
        # TODO: should sort according to accuracy too
        return sorted(answers,
                      key=lambda x:x.measures.get('relevance', DEFAULT_RELEVANCE),
                      reverse=True)

    def request_from_answer(self, answer):
        return Request(self.id, answer.language, answer.tree,
                       answer.measures, answer.trace)

    def one_pass(self, request):
        # First make all requests so modules can prepare their answer
        # while we send requests to other modules
        streams = self._get_streams(request)
        answers = map(self._stream_reader, streams)
        answers = map(self._process_answers, answers)
        answers = itertools.chain(*list(answers)) # Flatten answers lists
        answers = itertools.chain(self._get_python(request), answers)
        answers = filter(bool, answers) # Eliminate None values
        return answers

    def _get_python_class(self, url):
        (module_path, class_path) = url.split(':')
        cls = importlib.import_module(module_path)
        for token in class_path.split('.'):
            cls = getattr(cls, token)
        return cls

    def _get_python(self, request):
        for module in self.config.modules:
            if module.should_send(request) and module.method == 'python':
                try:
                    obj = self._get_python_class(module.url)(request)
                    for answer in obj.answer():
                        yield answer
                except KeyboardInterrupt:
                    raise
                except Exception:
                    tb = traceback.format_exc()
                    logger.error('Error in module %s\n: %s' % (module, tb))

    def _get_streams(self, request):
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json'}
        payload = request.as_json()
        getter = functools.partial(requests.post, stream=True,
                                   headers=headers, data=payload)
        streams = []
        for module in self.config.modules:
            try:
                if module.should_send(request) and module.method == 'http':
                    streams.append((module, getter(module.url)))
            except requests.exceptions.ConnectionError as exc: # pragma: no cover
                logger.warning('Module %s could not be queried: %s' %
                                (module, exc.args[0]))
                pass
        return streams

    def _stream_reader(self, stream):
        (module, stream) = stream
        if stream.status_code != 200:
            logger.warning('Module %s returned %d: %s' %
                            (module, stream.status_code, stream.content))
            return None
        else:
            try:
                return (module, json.loads(s(stream.content)))
            except ValueError:
                logger.warning('Module %s returned %d: %s' %
                                (module, stream.status_code, stream.content))
                return None
            finally:
                stream.close()

    def _process_answers(self, t):
        if t:
            (module, answers) = t
            answers = map(Response.from_dict, answers)
            return list(map(functools.partial(self._process_answer, module), answers))
        else:
            return []

    def _process_answer(self, module, answer):
        missing = {'accuracy', 'relevance'} - set(answer.measures)
        if missing:
            logger.warning('Missing mandatory measures from module %s: %r' %
                             (module, missing))
        accuracy = answer.measures.get('accuracy', DEFAULT_ACCURACY)
        relevance = answer.measures.get('relevance', DEFAULT_RELEVANCE)
        if accuracy < 0 or accuracy > 1:
            logger.warning('Module %s answered with invalid accuracy: %r' %
                    (module, accuracy))
            return None
        answer.measures['accuracy'] = accuracy
        answer.measures['relevance'] = relevance * module.coefficient
        return answer
