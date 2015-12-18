# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0005_test'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='blinded_mes',
            field=models.CharField(default=datetime.datetime(2015, 11, 30, 23, 34, 29, 879349, tzinfo=utc), max_length=2000),
            preserve_default=False,
        ),
    ]
