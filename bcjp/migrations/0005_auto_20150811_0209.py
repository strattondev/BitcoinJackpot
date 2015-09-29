# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bcjp', '0004_auto_20150802_0508'),
    ]

    operations = [
        migrations.AddField(
            model_name='bitcoinaddresssession',
            name='withdraw_address',
            field=models.CharField(default=b'', max_length=255),
        ),
        migrations.AlterField(
            model_name='bitcoinaddresssession',
            name='alias',
            field=models.CharField(default=b'taxpaying', max_length=255),
        ),
        migrations.AlterField(
            model_name='bitcoinwithdrawrequest',
            name='from_address',
            field=models.CharField(default=b'1PWF41FgmQT6eBr9s5pDdXokrtdeU3civ2', max_length=255),
        ),
        migrations.AlterField(
            model_name='rounds',
            name='winning_percent',
            field=models.FloatField(default=56.83671161243091),
        ),
    ]
