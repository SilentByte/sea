# #
# # SEA / SMART ENGINEERING ASSISTANT
# # Copyright (c) 2024 SilentByte <https://silentbyte.com/>
# #

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from core import status


def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'index.html', status=status.HTTP_503_SERVICE_UNAVAILABLE)
