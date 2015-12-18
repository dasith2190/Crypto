# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0006_test_blinded_mes'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='factor',
            field=models.FloatField(default=datetime.datetime(2015, 12, 1, 0, 13, 27, 923578, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='test',
            name='message',
            field=models.CharField(default=datetime.datetime(2015, 12, 1, 0, 13, 36, 191881, tzinfo=utc), max_length=2000),
            preserve_default=False,
        ),
    ]
