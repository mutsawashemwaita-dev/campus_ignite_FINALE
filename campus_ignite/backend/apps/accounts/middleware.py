from django.db import connections
from django.db.utils import OperationalError


class RetryDBConnectionMiddleware:
    """
    On Render's free tier, the app (and its DB connection) can go idle and
    get dropped mid-handshake right when the service wakes from a cold start.
    This catches that one-off failure and silently retries the request once
    with a fresh connection, so the user never sees the error.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except OperationalError:
            connections.close_all()
            return self.get_response(request)