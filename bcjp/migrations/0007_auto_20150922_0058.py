# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bcjp', '0006_auto_20150811_0212'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminBitcoinAddressSession',
            fields=[
                ('bitcoin_address_session', models.OneToOneField(primary_key=True, serialize=False, to='bcjp.BitcoinAddressSession')),
            ],
            options={
                'db_table': 'admin_bitcoin_address_session',
            },
        ),
        migrations.CreateModel(
            name='AdminOverride',
            fields=[
                ('uuid', models.CharField(default=b'd2b3c867-9842-4a7e-8a76-8bf482ea4322', max_length=36, serialize=False, primary_key=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('expires', models.DateTimeField(null=True)),
            ],
            options={
                'db_table': 'admin_override',
            },
        ),
        migrations.AlterField(
            model_name='bitcoinaddresssession',
            name='alias',
            field=models.CharField(default=b'proletarianisation', max_length=255),
        ),
        migrations.AlterField(
            model_name='rounds',
            name='winning_percent',
            field=models.FloatField(default=22.71484892912129),
        ),
    ]
