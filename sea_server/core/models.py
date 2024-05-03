# #
# # SEA / SMART ENGINEERING ASSISTANT
# # Copyright (c) 2024 SilentByte <https://silentbyte.com/>
# #

import os
import json

from uuid import uuid4

from django.contrib.admin import ModelAdmin
from django.contrib.auth.models import User
from django.db import models
from django.utils.html import format_html, escape

from core import utils


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


def truncate_format_text(text: str | None, max_length: int = 40) -> str:
    if text is None:
        return ''

    return format_html(
        r'<span title="{title}">{text}</span>',
        title=escape(text),
        text=escape(utils.truncate_ellipsis(text, max_length)),
    )


def monospace_format_text(text: str | None) -> str:
    if text is None:
        return ''

    return format_html(
        r'<small style="font-family: monospace">{text}</small>',
        text=escape(text),
    )


class DocumentAdmin(SeaModelAdmin):
    list_display = ['id', 'truncated_file_name', 'formatted_file_hash', 'formatted_file_size', 'file_creation_ts', 'file_modification_ts',
                    'last_checked_ts', 'last_synchronized_ts', 'created_on', 'last_modified_on']

    ordering = ['file_name', '-file_creation_ts']

    search_fields = ['id', 'file_name', 'file_hash']

    def truncated_file_name(self, instance) -> str:
        return truncate_format_text(os.path.basename(instance.file_name), 64)

    truncated_file_name.short_description = 'File'

    def formatted_file_hash(self, instance) -> str:
        return monospace_format_text(instance.file_hash)

    formatted_file_hash.short_description = 'SHA256'

    def formatted_file_size(self, instance) -> str:
        return f'{instance.file_size / 1024 / 1024:.2f}' + chr(0xA0) + 'MiB'

    formatted_file_size.short_description = 'Size'


class Document(models.Model):
    class Meta:
        db_table = 'document'
        indexes = [
            models.Index(fields=['file_name']),
            models.Index(fields=['file_creation_ts']),
        ]

    id = UUIDPrimaryKeyField()

    file_name = models.CharField(max_length=1024)

    file_hash = models.CharField(max_length=64,
                                 unique=True)

    file_size = models.PositiveBigIntegerField()

    file_creation_ts = models.DateTimeField()

    file_modification_ts = models.DateTimeField()

    last_checked_ts = models.DateTimeField(null=True,
                                           blank=True)

    last_synchronized_ts = models.DateTimeField(null=True,
                                                blank=True)

    created_on = CreatedOnField()

    last_modified_on = LastModifiedOnField()

    def __str__(self):
        return self.file_name


class InferenceLogAdmin(SeaModelAdmin):
    list_display = ['id', 'user', 'truncated_input', 'truncated_output', 'created_on', 'last_modified_on']

    list_select_related = ['user']

    ordering = ['-created_on']

    search_fields = ['id', 'file_name', 'file_hash']

    autocomplete_fields = ['user']

    def truncated_input(self, instance) -> str:
        return truncate_format_text(json.dumps(instance.input), 200)

    truncated_input.short_description = 'Input'

    def truncated_output(self, instance) -> str:
        return truncate_format_text(json.dumps(instance.output), 200)

    truncated_output.short_description = 'Output'


class InferenceLog(models.Model):
    class Meta:
        db_table = 'inference_log'
        indexes = [
            models.Index(fields=['created_on']),
        ]

    id = UUIDPrimaryKeyField()

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             null=True,
                             blank=True)

    input = models.JSONField()

    output = models.JSONField()

    created_on = CreatedOnField()

    last_modified_on = LastModifiedOnField()

    def __str__(self):
        return str(self.id)
