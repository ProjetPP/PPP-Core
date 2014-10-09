"""Handles the HTTP frontend (ie. answers to requests from a
UI."""

import json
from .router import Router
from .settings import DEBUG
from .exceptions import ClientError

DOC_URL = 'https://github.com/ProjetPP/Documentation/blob/master/' \
          'module-communication.md#frontend'

def make_response(start_response, status, content_type, response):
    """Shortcut for making a response to the client's request."""
    start_response(status, [('Content-type', content_type)])
    return [response.encode()]

def on_bad_method(start_response):
    """Returns a basic response to GET requests (probably sent by humans
    trying to open the link in a web browser."""
    return make_response(start_response,
                         '405 Method Not Allowed',
                         'text/plain',
                         'Bad method, only POST is supported. See: ' + DOC_URL
                        )

def on_unknown_uri(start_response):
    """Returns a basic response to GET requests (probably sent by humans
    trying to open the link in a web browser."""
    return make_response(start_response,
                         '404 Not Found',
                         'text/plain',
                         'URI not found, only / is supported. See: ' + DOC_URL
                        )

def on_bad_request(hint, start_response):
    """Returns a basic response to invalid requests."""
    return make_response(start_response,
                         '400 Bad Request',
                         'text/plain',
                         hint
                        )

def on_client_error(exc, start_response):
    """Handler for any error in the request detected by the core."""
    return on_bad_request(exc.args[0], start_response)

def on_internal_error(start_response): # pragma: no cover
    """Returns a basic response when the core crashed"""
    return make_response(start_response,
                         '500 Internal Server Error',
                         'text/plain',
                         'Internal server error. Sorry :/'
                        )

def process_request(request, start_response):
    """Processes a request."""
    try:
        request = json.loads(request.read().decode())
    except ValueError:
        raise ClientError('Data is not valid JSON.')
    answer = Router(request).answer()
    return make_response(start_response,
                         '200 OK',
                         'application/json',
                         json.dumps(answer)
                        )

def on_post(environ, start_response):
    """Extracts the request, feeds the core, and returns the response."""
    request = environ['wsgi.input']
    try:
        return process_request(request, start_response)
    except ClientError as exc:
        return on_client_error(exc, start_response)
    except Exception: # pragma: no cover # pylint: disable=W0703
        if DEBUG:
            raise
        else:
            return on_internal_error(start_response)


def app(environ, start_response):
    """Function called by the WSGI server."""
    if environ['PATH_INFO'] != '/':
        return on_unknown_uri(start_response)
    elif environ['REQUEST_METHOD'] == 'POST':
        return on_post(environ, start_response)
    else:
        return on_bad_method(start_response)

