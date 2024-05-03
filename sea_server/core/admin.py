# #
# # SEA / SMART ENGINEERING ASSISTANT
# # Copyright (c) 2024 SilentByte <https://silentbyte.com/>
# #

from django.contrib import admin
from core import models

admin.site.register(models.UserAccount, models.UserAccountAdmin)
admin.site.register(models.AuthToken, models.AuthTokenAdmin)
admin.site.register(models.Document, models.DocumentAdmin)
admin.site.register(models.InferenceLog, models.InferenceLogAdmin)
