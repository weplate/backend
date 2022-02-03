from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse

import functools


def json_response(data: dict[str, object], error: bool = False, message: str = 'Success') -> JsonResponse:
    return JsonResponse(
        data=data | {
            'error': error,
            'message': message
        }
    )


def ok_response(message: str = 'success'):
    return json_response({}, False, message)


def err_response(message: str):
    return json_response({}, True, message)


def auth_endpoint(table):
    """
    Decorator for endpoints that require authentication
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(request: WSGIRequest):
            if request.user.is_authenticated():
                if table.objects.filter(user__id=request.user.id).exists():
                    return func(request)
                else:
                    return err_response('Not authenticated')
            else:
                return err_response('Not authenticated')
        return wrapper

    return decorator
