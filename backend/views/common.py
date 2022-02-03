from django.http import JsonResponse


def json_response(data: dict[str, object], error: bool = False, message: str = 'Success') -> JsonResponse:
    return JsonResponse(
        data=data | {
            'error': error,
            'message': message
        }
    )


def ok_response():
    return json_response({})


def err_response(message: str):
    return json_response({}, True, message)