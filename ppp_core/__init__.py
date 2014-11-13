"""Core/router of the Projet Pensées Profondes."""

from ppp_libmodule.http import HttpRequestHandler
from .router import Router

def app(environ, start_response):
    """Function called by the WSGI server."""
    r = HttpRequestHandler(environ, start_response, Router).dispatch()
    return r
