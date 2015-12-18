# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0002_auto_20151129_0458'),
    ]

    operations = [
        migrations.CreateModel(
            name='Envelope',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.CharField(max_length=2000)),
                ('blinding_factor', models.FloatField()),
                ('message_id', models.IntegerField()),
                ('message_num', models.IntegerField()),
            ],
        ),
    ]
