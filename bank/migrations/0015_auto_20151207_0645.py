# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0014_serial_number_merchant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serial_number_merchant',
            name='merchant',
            field=models.CharField(max_length=9),
        ),
    ]
