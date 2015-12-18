# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0008_auto_20151201_0015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='envelope',
            name='blinding_factor',
            field=models.DecimalField(max_digits=500, decimal_places=2),
        ),
    ]
