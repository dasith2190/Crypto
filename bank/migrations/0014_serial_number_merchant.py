# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0013_envelope_msg_blinded'),
    ]

    operations = [
        migrations.CreateModel(
            name='serial_number_merchant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('id_string', models.CharField(max_length=500)),
                ('merchant', models.ForeignKey(to='bank.user_account')),
                ('serial_number', models.ForeignKey(to='bank.serial_numbers')),
            ],
        ),
    ]
