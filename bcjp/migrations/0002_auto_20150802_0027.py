# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bcjp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bitcoinaddresssession',
            name='alias',
            field=models.CharField(default=b'distractedly', max_length=255),
        ),
        migrations.AlterField(
            model_name='rounds',
            name='winning_percent',
            field=models.FloatField(default=86.88224574668168),
        ),
    ]
