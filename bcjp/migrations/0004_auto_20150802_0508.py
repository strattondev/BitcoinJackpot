# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bcjp', '0003_auto_20150802_0307'),
    ]

    operations = [
        migrations.CreateModel(
            name='BitcoinBet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.BigIntegerField(default=0)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'bitcoin_bet',
            },
        ),
        migrations.AlterField(
            model_name='bitcoinaddresssession',
            name='alias',
            field=models.CharField(default=b'afield', max_length=255),
        ),
        migrations.AlterField(
            model_name='rounds',
            name='winning_percent',
            field=models.FloatField(default=5.133049190309645),
        ),
        migrations.AddField(
            model_name='bitcoinbet',
            name='bitcoin_address_session',
            field=models.ForeignKey(to='bcjp.BitcoinAddressSession'),
        ),
        migrations.AddField(
            model_name='roundlog',
            name='bet',
            field=models.ForeignKey(default=None, to='bcjp.BitcoinBet', null=True),
        ),
    ]
