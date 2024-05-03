# #
# # SEA / SMART ENGINEERING ASSISTANT
# # Copyright (c) 2024 SilentByte <https://silentbyte.com/>
# #

from django.http import (
    HttpRequest,
    HttpResponse,
)

from django.shortcuts import render

from core import (
    status,
    businesslogic,
)


class HttpMethodNotAllowedResponse(HttpResponse):
    def __init__(self):
        super().__init__(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class HttpNotFoundResponse(HttpResponse):
    def __init__(self):
        super().__init__(status=status.HTTP_404_NOT_FOUND)


def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'index.html', status=status.HTTP_503_SERVICE_UNAVAILABLE)


def document(request: HttpRequest, file_hash: str) -> HttpResponse:
    if request.method != 'GET':
        return HttpMethodNotAllowedResponse()

    file_name = businesslogic.get_document_path(file_hash)

    if file_name is None:
        return HttpNotFoundResponse()

    with open(file_name, 'rb') as fp:
        return HttpResponse(fp)
