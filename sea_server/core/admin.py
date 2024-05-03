# #
# # SEA / SMART ENGINEERING ASSISTANT
# # Copyright (c) 2024 SilentByte <https://silentbyte.com/>
# #

from django.contrib.admin import AdminSite
from django.contrib.auth import (
    admin as auth_admin,
    models as auth_models
)

from core import models

site = AdminSite(name='admin')

site.register(auth_models.User, auth_admin.UserAdmin)
site.register(auth_models.Group, auth_admin.GroupAdmin)

site.register(models.Document, models.DocumentAdmin)
