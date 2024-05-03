# #
# # SEA / SMART ENGINEERING ASSISTANT
# # Copyright (c) 2024 SilentByte <https://silentbyte.com/>
# #

from django.contrib import admin
from django.urls import path

from core import views

urlpatterns = [
    path('records/', admin.site.urls),
    path('api/authenticate', views.authenticate),
    path('api/document/<str:file_hash>', views.download_document),
    path('api/search_documents', views.search_documents),
    path('api/inference/query', views.inference_query),
    path('', views.index),
]
