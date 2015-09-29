# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bcjp', '0007_auto_20150922_0058'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminBitcoinBet',
            fields=[
                ('bitcoin_bet', models.OneToOneField(primary_key=True, serialize=False, to='bcjp.BitcoinBet')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'admin_bitcoin_bet',
            },
        ),
        migrations.AlterField(
            model_name='adminoverride',
            name='uuid',
            field=models.CharField(default=b'823012c3-acd1-4f25-80b1-b01d79efe8a2', max_length=36, serialize=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='bitcoinaddresssession',
            name='alias',
            field=models.CharField(default=b'irreverently', max_length=255),
        ),
        migrations.AlterField(
            model_name='rounds',
            name='winning_percent',
            field=models.FloatField(default=23.230368026476867),
        ),
    ]
