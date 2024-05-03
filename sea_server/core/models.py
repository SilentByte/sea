# #
# # SEA / SMART ENGINEERING ASSISTANT
# # Copyright (c) 2024 SilentByte <https://silentbyte.com/>
# #


from uuid import uuid4

from django.contrib.admin import ModelAdmin
from django.db import models


class UUIDPrimaryKeyField(models.UUIDField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('primary_key', True)
        kwargs.setdefault('default', uuid4)
        kwargs.setdefault('editable', False)
        super().__init__(*args, **kwargs)


class CreatedOnField(models.DateTimeField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('auto_now_add', True)
        super().__init__(*args, **kwargs)


class LastModifiedOnField(models.DateTimeField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('auto_now', True)
        super().__init__(*args, **kwargs)


class SeaModelAdmin(ModelAdmin):
    list_per_page = 100
    list_max_show_all = 1000
    actions_on_top = True
    actions_on_bottom = True


class DocumentAdmin(SeaModelAdmin):
    list_display = ['id', 'file_name', 'file_hash', 'file_size', 'file_creation_ts', 'file_modification_ts',
                    'created_on', 'last_modified_on']

    ordering = ['file_name', '-file_creation_ts']

    search_fields = ['id', 'file_name', 'file_hash']


class Document(models.Model):
    class Meta:
        db_table = 'document'
        indexes = [
            models.Index(fields=['file_name']),
            models.Index(fields=['file_hash']),
            models.Index(fields=['file_creation_ts']),
        ]

    id = UUIDPrimaryKeyField()

    file_name = models.CharField(max_length=1024)

    file_hash = models.CharField(max_length=64)

    file_size = models.PositiveBigIntegerField()

    file_creation_ts = models.DateTimeField()

    file_modification_ts = models.DateTimeField()

    created_on = CreatedOnField()

    last_modified_on = LastModifiedOnField()

    def __str__(self):
        return self.file_name
