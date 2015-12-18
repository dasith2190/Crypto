# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0009_auto_20151201_0148'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Test',
        ),
    ]
