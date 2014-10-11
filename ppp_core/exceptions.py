"""Exceptions of the PPP Core."""

class ClientError(Exception):
    """Exception raised by the router for showing an error to the
    client."""
    pass

class InvalidConfig(Exception):
    """Exception raised when there is an error in the config."""
    pass
