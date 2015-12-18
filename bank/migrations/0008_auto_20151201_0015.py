# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0007_auto_20151201_0013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='factor',
            field=models.CharField(max_length=2000),
        ),
    ]
