# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0010_delete_test'),
    ]

    operations = [
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('md5', models.CharField(max_length=2000)),
                ('blinded_mes', models.CharField(max_length=2000)),
                ('message', models.CharField(max_length=2000)),
                ('factor', models.CharField(max_length=2000)),
                ('message_id', models.IntegerField()),
                ('message_num', models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='envelope',
            name='blinding_factor',
            field=models.CharField(max_length=5000),
        ),
    ]
