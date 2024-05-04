# #
# # SEA / SMART ENGINEERING ASSISTANT
# # Copyright (c) 2024 SilentByte <https://silentbyte.com/>
# #

import re
import json

from django.http import (
    HttpRequest,
    HttpResponse,
    JsonResponse,
)

from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from sea.inference import InferenceInteraction

from server import settings

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


class HttpUnsupportedMediaTypeResponse(HttpResponse):
    def __init__(self):
        super().__init__(status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)


class HttpUnauthorizedResponse(HttpResponse):
    def __init__(self):
        super().__init__(status=status.HTTP_401_UNAUTHORIZED)


def extract_token(request: HttpRequest) -> str | None:
    header = request.META.get('HTTP_AUTHORIZATION', None)

    if header is None:
        return request.COOKIES.get('X-Authorization-Token', None)

    match = re.match(r'^Bearer\s+([0-9a-zA-Z_\-]+)\s*$', header)
    if not match:
        return None

    return match.group(1)


@csrf_exempt
def index(request: HttpRequest) -> HttpResponse:
    if settings.DEBUG:
        return redirect('http://localhost:5173')

    return render(request, 'index.html', status=status.HTTP_503_SERVICE_UNAVAILABLE)


@csrf_exempt
def authenticate(request: HttpRequest) -> HttpResponse:
    if request.method != 'POST':
        return HttpMethodNotAllowedResponse()

    if request.content_type != 'application/json':
        return HttpUnsupportedMediaTypeResponse()

    body = json.loads(request.body)
    email = body['email']
    credentials = body['credentials']

    authentication = businesslogic.authenticate_with_credentials(email, credentials)

    if authentication is None:
        return HttpUnauthorizedResponse()

    return JsonResponse({
        'display_name': authentication[0].display_name,
        'token': authentication[1].token,
    })


@csrf_exempt
def download_document(request: HttpRequest, file_hash: str) -> HttpResponse:
    if request.method != 'GET':
        return HttpMethodNotAllowedResponse()

    if businesslogic.authenticate_with_token(extract_token(request)) is None:
        return HttpUnauthorizedResponse()

    file_name = businesslogic.get_document_path(file_hash)

    if file_name is None:
        return HttpNotFoundResponse()

    with open(file_name, 'rb') as fp:
        return HttpResponse(fp, content_type='application/pdf')


@csrf_exempt
def search_documents(request: HttpRequest) -> HttpResponse:
    if request.method != 'GET':
        return HttpMethodNotAllowedResponse()

    if businesslogic.authenticate_with_token(extract_token(request)) is None:
        return HttpUnauthorizedResponse()

    body = json.loads(request.body)

    return JsonResponse([
        di.to_dict()
        for di in businesslogic.search_documents(body['query'])
    ], safe=False)


@csrf_exempt
def inference_search(request: HttpRequest) -> HttpResponse:
    if request.method != 'POST':
        return HttpMethodNotAllowedResponse()

    if request.content_type != 'application/json':
        return HttpUnsupportedMediaTypeResponse()

    if businesslogic.authenticate_with_token(extract_token(request)) is None:
        return HttpUnauthorizedResponse()

    body = json.loads(request.body)

    return JsonResponse([
        di.to_dict()
        for di in businesslogic.execute_inference_vector_search(body['query'])
    ], safe=False)


@csrf_exempt
def inference_query(request: HttpRequest) -> HttpResponse:
    if request.method != 'POST':
        return HttpMethodNotAllowedResponse()

    if request.content_type != 'application/json':
        return HttpUnsupportedMediaTypeResponse()

    if (user := businesslogic.authenticate_with_token(extract_token(request))) is None:
        return HttpUnauthorizedResponse()

    body = json.loads(request.body)

    inference_result = businesslogic.execute_inference_query(
        user=user,
        inference_interactions=[
            InferenceInteraction(ii['originator'], ii['text'])
            for ii in body['inference_interactions']
        ],
    )

    return JsonResponse(inference_result.to_dict())
