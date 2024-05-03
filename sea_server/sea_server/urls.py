# #
# # SEA / SMART ENGINEERING ASSISTANT
# # Copyright (c) 2024 SilentByte <https://silentbyte.com/>
# #

from django.contrib import admin
from django.urls import path

from core import views

urlpatterns = [
    path('records/', admin.site.urls),
    path('', views.index),
]
