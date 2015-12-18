# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0011_auto_20151201_0201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='envelope',
            name='blinding_factor',
            field=models.CharField(max_length=4000),
        ),
    ]
