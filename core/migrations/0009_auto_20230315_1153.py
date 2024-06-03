# Generated by Django 3.2.18 on 2023-03-15 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_regenerate_user_wallets'),
    ]

    operations = [
        migrations.AddField(
            model_name='feesandlimits',
            name='limits_accumulation_max_gas_price',
            field=models.DecimalField(decimal_places=16, default=0, help_text='Gwei', max_digits=32),
        ),
        migrations.AlterField(
            model_name='wallettransactions',
            name='state',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Created'), (2, 'Verification failed'), (3, 'Waiting for KYT approve'), (4, 'KYT approve on check'), (5, 'KYT approve platform error'), (6, 'KYT approve rejected'), (7, 'Waiting for accumulation'), (8, 'Gas Required'), (9, 'Waiting for gas'), (10, 'Ready for accumulation'), (11, 'Accumulation in progress'), (12, 'Accumulated'), (13, 'Balance too low'), (14, 'Manual deposit'), (15, 'Old wallet deposit'), (16, 'External accumulated'), (17, 'Gas price too high')], default=1),
        ),
    ]
