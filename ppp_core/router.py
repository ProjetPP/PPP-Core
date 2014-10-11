"""Router of the PPP core."""

import json
import logging
import requests
import operator
import functools
from .config import Config
from .exceptions import ClientError

class Router:
    def __init__(self, request):
        self.extract_request(request)
        self.config = Config()

    def extract_request(self, request):
        try:
            self.language = request['language']
            self.tree = request['tree']
        except KeyError:
            raise ClientError('Missing mandatory field in request object.')

    def answer(self):
        # First make all requests so modules can prepare their answer
        # while we send requests to other modules
        streams = self._get_streams()
        answers = map(lambda x:(x[0], json.loads(x[1].content)), streams)
        answers = list(filter(bool, map(self._process_answer, answers)))
        if answers:
            return max(answers, key=operator.itemgetter('pertinence'))
        else:
            return {'language': self.language, 'pertinence': 0, 'tree': self.tree}

    def _get_streams(self):
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json'}
        payload = json.dumps({'language': self.language, 'tree': self.tree})
        getter = functools.partial(requests.get, stream=True,
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

    def _process_answer(self, t):
        (module, answer) = t
        pertinence = answer['pertinence']
        if not isinstance(pertinence, int) and \
                not isinstance(pertinence, float) and \
                pertinence < 0 or pertinence > 1:
            logging.warning('Module %s answered with invalid pertinence: %r' %
                    (module, pertinence))
            return None
        answer['pertinence'] *= module.coefficient
        return answer
