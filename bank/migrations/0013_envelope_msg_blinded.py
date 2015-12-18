# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0012_auto_20151201_0203'),
    ]

    operations = [
        migrations.AddField(
            model_name='envelope',
            name='msg_blinded',
            field=models.CharField(default='before', max_length=4000),
            preserve_default=False,
        ),
    ]
