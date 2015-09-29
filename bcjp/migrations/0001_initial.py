# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BitcoinAddressSession',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.CharField(unique=True, max_length=255)),
                ('session', models.CharField(default=b'', max_length=255)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('amount', models.BigIntegerField(default=0)),
            ],
            options={
                'db_table': 'bitcoin_address_session',
            },
        ),
        migrations.CreateModel(
            name='BitcoinPaymentCompleted',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.BigIntegerField(default=0)),
                ('input_address', models.CharField(max_length=255)),
                ('confirmations', models.IntegerField(default=6)),
                ('transaction_hash', models.CharField(max_length=255)),
                ('input_transaction_hash', models.CharField(max_length=255)),
                ('destination_address', models.CharField(max_length=255)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'bitcoin_payment_completed',
            },
        ),
        migrations.CreateModel(
            name='BitcoinPaymentPending',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.BigIntegerField(default=0)),
                ('input_address', models.CharField(max_length=255)),
                ('confirmations', models.IntegerField(default=0)),
                ('transaction_hash', models.CharField(max_length=255)),
                ('input_transaction_hash', models.CharField(max_length=255)),
                ('destination_address', models.CharField(max_length=255)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'bitcoin_payment_pending',
            },
        ),
        migrations.CreateModel(
            name='RoundLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField()),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('is_bet', models.BooleanField(default=False)),
                ('is_start', models.BooleanField(default=False)),
                ('is_end', models.BooleanField(default=False)),
                ('is_winner', models.BooleanField(default=False)),
                ('payment', models.ForeignKey(default=None, to='bcjp.BitcoinPaymentCompleted', null=True)),
            ],
            options={
                'db_table': 'round_log',
            },
        ),
        migrations.CreateModel(
            name='Rounds',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('secret_hash', models.CharField(unique=True, max_length=48)),
                ('winning_percent', models.FloatField(default=22.091715030783664)),
                ('round_hash', models.CharField(max_length=255)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'rounds',
            },
        ),
        migrations.CreateModel(
            name='RoundWinner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('total', models.BigIntegerField(default=0)),
                ('cut', models.BigIntegerField(default=0)),
                ('winnings', models.BigIntegerField(default=0)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('bitcoin_address_session', models.ForeignKey(to='bcjp.BitcoinAddressSession')),
                ('round', models.ForeignKey(to='bcjp.Rounds')),
            ],
            options={
                'db_table': 'round_winner',
            },
        ),
        migrations.AddField(
            model_name='roundlog',
            name='round',
            field=models.ForeignKey(to='bcjp.Rounds'),
        ),
    ]
