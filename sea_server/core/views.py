# #
# # SEA / SMART ENGINEERING ASSISTANT
# # Copyright (c) 2024 SilentByte <https://silentbyte.com/>
# #

import json

from django.http import (
    HttpRequest,
    HttpResponse,
    JsonResponse,
)

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from sea.inference import InferenceInteraction

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


class HttpUnsupportedMediaType(HttpResponse):
    def __init__(self):
        super().__init__(status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)


@csrf_exempt
def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'index.html', status=status.HTTP_503_SERVICE_UNAVAILABLE)


@csrf_exempt
def document(request: HttpRequest, file_hash: str) -> HttpResponse:
    if request.method != 'GET':
        return HttpMethodNotAllowedResponse()

    file_name = businesslogic.get_document_path(file_hash)

    if file_name is None:
        return HttpNotFoundResponse()

    with open(file_name, 'rb') as fp:
        return HttpResponse(fp)


@csrf_exempt
def inference_query(request: HttpRequest) -> HttpResponse:
    if request.method != 'POST':
        return HttpMethodNotAllowedResponse()

    if request.content_type != 'application/json':
        return HttpUnsupportedMediaType()

    body = json.loads(request.body)

    inference_result = businesslogic.execute_inference_query(
        user=None,
        inference_interactions=[
            InferenceInteraction(ii['originator'], ii['text'])
            for ii in body['inference_interactions']
        ],
    )

    return JsonResponse(inference_result.to_dict())
