# Generated by Django 5.0.4 on 2024-05-03 05:08

import core.models
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', core.models.UUIDPrimaryKeyField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('file_name', models.CharField(max_length=1024)),
                ('file_hash', models.CharField(max_length=64)),
                ('file_size', models.PositiveBigIntegerField()),
                ('file_creation_ts', models.DateTimeField()),
                ('file_modification_ts', models.DateTimeField()),
                ('created_on', core.models.CreatedOnField(auto_now_add=True)),
                ('last_modified_on', core.models.LastModifiedOnField(auto_now=True)),
            ],
            options={
                'db_table': 'document',
                'indexes': [models.Index(fields=['file_name'], name='document_file_na_c72421_idx'), models.Index(fields=['file_hash'], name='document_file_ha_c9291e_idx'), models.Index(fields=['file_creation_ts'], name='document_file_cr_aa25c1_idx')],
            },
        ),
    ]
