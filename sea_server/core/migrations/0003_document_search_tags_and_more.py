# Generated by Django 5.0.4 on 2024-05-03 14:56

import django.contrib.postgres.fields
import django.contrib.postgres.indexes
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_authtoken_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='search_tags',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), default=[], size=None),
            preserve_default=False,
        ),
        migrations.AddIndex(
            model_name='document',
            index=django.contrib.postgres.indexes.GinIndex(fields=['search_tags'], name='document_search__0b238f_gin'),
        ),
    ]