# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bcjp', '0002_auto_20150802_0027'),
    ]

    operations = [
        migrations.CreateModel(
            name='BitcoinWithdrawRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.BigIntegerField(default=0)),
                ('to_address', models.CharField(max_length=255)),
                ('from_address', models.CharField(default=b'15j23joNcJxRXqv5Jcjp2DBu9uzBZcNaXR', max_length=255)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('transaction_hash', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'bitcoin_withdraw_request',
            },
        ),
        migrations.AlterField(
            model_name='bitcoinaddresssession',
            name='alias',
            field=models.CharField(default=b'chainsaw', max_length=255),
        ),
        migrations.AlterField(
            model_name='rounds',
            name='winning_percent',
            field=models.FloatField(default=90.04591227070476),
        ),
        migrations.AddField(
            model_name='bitcoinwithdrawrequest',
            name='bitcoin_address_session',
            field=models.ForeignKey(to='bcjp.BitcoinAddressSession'),
        ),
    ]
