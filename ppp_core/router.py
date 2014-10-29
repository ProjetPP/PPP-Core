"""Router of the PPP core."""

import json
import logging
import requests
import operator
import itertools
import functools
from ppp_datamodel.communication import Request, Response
from .config import Config
from .exceptions import ClientError, BadGateway

s = lambda x:x if isinstance(x, str) else x.decode()

class Router:
    def __init__(self, request):
        self.language = request.language
        self.tree = request.tree
        self.config = Config()

    def answer(self):
        # First make all requests so modules can prepare their answer
        # while we send requests to other modules
        streams = self._get_streams()
        answers = map(self._stream_reader, streams)
        answers = map(self._process_answers, answers)
        answers = itertools.chain(*list(answers)) # Flatten answers lists
        answers = filter(bool, answers) # Eliminate None values
        # TODO: should sort according to accuracy too
        return sorted(answers, key=lambda x:x.measures['relevance'],
                      reverse=True)

    def _get_streams(self):
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json'}
        payload = Request(self.language, self.tree).as_json()
        getter = functools.partial(requests.post, stream=True,
                                   headers=headers, data=payload)
        streams = []
        for module in self.config.modules:
            try:
                streams.append((module, getter(module.url)))
            except requests.exceptions.ConnectionError as exc: # pragma: no cover
                logging.warning('Module %s could not be queried: %s' %
                                (module, exc.args[0]))
                pass
        return streams

    def _stream_reader(self, stream):
        (module, stream) = stream
        if stream.status_code != 200:
            logging.warning('Module %s returned %d: %s' %
                            (module, stream.status_code, stream.content))
            return None
        else:
            return (module, json.loads(s(stream.content)))

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
            raise BadGateway('Missing mandatory measures from a module: %r' %
                             missing)
        accuracy = answer.measures['accuracy']
        if accuracy < 0 or accuracy > 1:
            logging.warning('Module %s answered with invalid accuracy: %r' %
                    (module, accuracy))
            return None
        answer.measures['relevance'] *= module.coefficient
        return answer
