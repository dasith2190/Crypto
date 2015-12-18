# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0004_server_envelope'),
    ]

    operations = [
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('md5', models.CharField(max_length=2000)),
                ('message_id', models.IntegerField()),
                ('message_num', models.IntegerField()),
            ],
        ),
    ]
