"""Handles the HTTP frontend (ie. answers to requests from a
UI."""

import json
import logging

from .router import Router
from .config import Config
from .exceptions import ClientError, InvalidConfig

DOC_URL = 'https://github.com/ProjetPP/Documentation/blob/master/' \
          'module-communication.md#frontend'

class HttpRequestHandler:
    """Handles one request."""
    def __init__(self, environ, start_response, router_class):
        self.environ = environ
        self.start_response = start_response
        self.router_class = router_class
    def make_response(self, status, content_type, response):
        """Shortcut for making a response to the client's request."""
        self.start_response(status, [('Content-type', content_type)])
        return [response.encode()]

    def on_bad_method(self):
        """Returns a basic response to GET requests (probably sent by humans
        trying to open the link in a web browser."""
        text = 'Bad method, only POST is supported. See: ' + DOC_URL
        return self.make_response('405 Method Not Allowed',
                                  'text/plain',
                                  text
                                 )

    def on_unknown_uri(self):
        """Returns a basic response to GET requests (probably sent by humans
        trying to open the link in a web browser."""
        text = 'URI not found, only / is supported. See: ' + DOC_URL
        return self.make_response('404 Not Found',
                                  'text/plain',
                                  text
                                 )

    def on_bad_request(self, hint):
        """Returns a basic response to invalid requests."""
        return self.make_response('400 Bad Request',
                                  'text/plain',
                                  hint
                                 )

    def on_client_error(self, exc):
        """Handler for any error in the request detected by the core."""
        return self.on_bad_request(exc.args[0])

    def on_internal_error(self): # pragma: no cover
        """Returns a basic response when the core crashed"""
        return self.make_response('500 Internal Server Error',
                                  'text/plain',
                                  'Internal server error. Sorry :/'
                                 )

    def process_request(self, request):
        """Processes a request."""
        try:
            request = json.loads(request.read().decode())
        except ValueError:
            raise ClientError('Data is not valid JSON.')
        answer = self.router_class(request).answer()
        return self.make_response('200 OK',
                                  'application/json',
                                  json.dumps(answer)
                                 )

    def on_post(self):
        """Extracts the request, feeds the core, and returns the response."""
        request = self.environ['wsgi.input']
        try:
            return self.process_request(request)
        except ClientError as exc:
            return self.on_client_error(exc)
        except InvalidConfig:
            raise
        except Exception as exc: # pragma: no cover # pylint: disable=W0703
            logging.error('Unknown exception: ', exc_info=exc)
            return self.on_internal_error()


    def dispatch(self):
        """Handles dispatching of the request."""
        if self.environ['PATH_INFO'] != '/':
            return self.on_unknown_uri()
        elif self.environ['REQUEST_METHOD'] == 'POST':
            return self.on_post()
        else:
            return self.on_bad_method()

def app(environ, start_response):
    """Function called by the WSGI server."""
    return HttpRequestHandler(environ, start_response, Router).dispatch()
