"""Router of the PPP core."""

from .exceptions import ClientError

class Router:
    def __init__(self, request):
        self.extract_request(request)

    def extract_request(self, request):
        try:
            self.language = request['language']
            self.tree = request['tree']
        except KeyError:
            raise ClientError('Missing mandatory field in request object.')

    def answer(self):
        return {'language': self.language, 'pertinence': 0, 'tree': self.tree}
