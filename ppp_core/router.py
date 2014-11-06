"""Router of the PPP core."""

import json
import logging
import requests
import operator
import itertools
import functools
from ppp_datamodel import AbstractNode
from ppp_datamodel.communication import Request, Response
from .config import CoreConfig
from .exceptions import ClientError, BadGateway

s = lambda x:x if isinstance(x, str) else x.decode()

DEFAULT_ACCURACY = 0
DEFAULT_RELEVANCE = 0

def answer_id(answer):
    return (answer.language, answer.tree,
            frozenset(answer.measures.items()),
            answer.tree)
def remove_duplicates(reference, new):
    return filter(lambda x:answer_id(x) not in reference, new)


class Router:
    def __init__(self, request):
        self.id = request.id
        self.language = request.language
        assert isinstance(request.tree, AbstractNode)
        self.tree = request.tree
        self.measures = request.measures
        self.trace = request.trace
        self.config = CoreConfig()

    def answer(self):
        answer_ids = set()
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
            new_answers = list(remove_duplicates(answers, new_answers))
            answers.extend(new_answers)
            answer_ids.update(map(answer_id, new_answers))
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
        answers = filter(bool, answers) # Eliminate None values
        return answers

    def _get_streams(self, request):
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json'}
        payload = request.as_json()
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
            logging.warning('Missing mandatory measures from module %s: %r' %
                             (module, missing))
        accuracy = answer.measures.get('accuracy', DEFAULT_ACCURACY)
        relevance = answer.measures.get('relevance', DEFAULT_RELEVANCE)
        if accuracy < 0 or accuracy > 1:
            logging.warning('Module %s answered with invalid accuracy: %r' %
                    (module, accuracy))
            return None
        answer.measures['accuracy'] = accuracy
        answer.measures['relevance'] = relevance * module.coefficient
        return answer
