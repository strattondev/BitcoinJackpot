# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bcjp', '0005_auto_20150811_0209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bitcoinaddresssession',
            name='alias',
            field=models.CharField(default=b'congest', max_length=255),
        ),
        migrations.AlterField(
            model_name='bitcoinaddresssession',
            name='withdraw_address',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='rounds',
            name='winning_percent',
            field=models.FloatField(default=69.90753216048104),
        ),
    ]
