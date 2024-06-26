# Generated by Django 3.2.7 on 2022-08-12 12:45

import core.pairs
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import lib.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LiquidityMatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('pair', core.pairs.PairModelField()),
                ('quantity', lib.fields.MoneyField(decimal_places=12, max_digits=32)),
                ('main_exchange_price', lib.fields.MoneyField(decimal_places=12, max_digits=32)),
                ('binance_price', lib.fields.MoneyField(decimal_places=12, max_digits=32)),
                ('side', models.PositiveSmallIntegerField(choices=[(1, 'Buy'), (2, 'Sell')], default=1)),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Complete'), (2, 'Failed')], default=1)),
            ],
        ),
        migrations.CreateModel(
            name='LiquidityStat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('deals', models.PositiveIntegerField(default=0)),
                ('btc_change', lib.fields.MoneyField(decimal_places=12, max_digits=32)),
                ('eth_change', lib.fields.MoneyField(decimal_places=12, max_digits=32)),
                ('profit', lib.fields.MoneyField(decimal_places=2, max_digits=32)),
            ],
        ),
        migrations.CreateModel(
            name='OrderMatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('pair', core.pairs.PairModelField()),
                ('quantity', lib.fields.MoneyField(decimal_places=12, max_digits=32)),
                ('price', lib.fields.MoneyField(decimal_places=12, max_digits=32)),
                ('side', models.PositiveSmallIntegerField(choices=[(1, 'Buy'), (2, 'Sell')], default=1)),
            ],
        ),
        migrations.CreateModel(
            name='OrderMatchStat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('deals', models.PositiveIntegerField(default=0)),
                ('pair', core.pairs.PairModelField()),
                ('total_buy', lib.fields.MoneyField(decimal_places=12, max_digits=32)),
                ('total_sell', lib.fields.MoneyField(decimal_places=12, max_digits=32)),
                ('change', lib.fields.MoneyField(decimal_places=12, max_digits=32)),
            ],
        ),
        migrations.CreateModel(
            name='BotConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('pair', core.pairs.PairModelField()),
                ('strategy', models.CharField(choices=[('trade_draw_graph', 'Draw graph'), ('liquidity', 'Liquidity Provider'), ('order_creation', 'Order Creation'), ('ohlc', 'OHLC')], default='trade_draw_graph', max_length=255)),
                ('symbol_precision', models.IntegerField(default=4)),
                ('quote_precision', models.IntegerField(default=4)),
                ('loop_period', models.IntegerField(default=10)),
                ('loop_period_random', models.BooleanField(default=False)),
                ('min_period', models.PositiveSmallIntegerField(default=30, validators=[django.core.validators.MinValueValidator(5)], verbose_name='Min period in seconds')),
                ('max_period', models.PositiveSmallIntegerField(default=60, validators=[django.core.validators.MinValueValidator(5)], verbose_name='Max period in seconds')),
                ('ext_price_delta', lib.fields.MoneyField(decimal_places=12, default=0.001, max_digits=32)),
                ('min_order_quantity', lib.fields.MoneyField(decimal_places=12, default=0.1, max_digits=32)),
                ('max_order_quantity', lib.fields.MoneyField(decimal_places=12, default=0.5, max_digits=32)),
                ('enabled', models.BooleanField(default=True)),
                ('stopped', models.BooleanField(default=False)),
                ('match_user_orders', models.BooleanField(default=False)),
                ('next_launch', models.DateTimeField(blank=True)),
                ('instant_match', models.BooleanField(default=False)),
                ('use_custom_price', models.BooleanField(default=False)),
                ('custom_price', lib.fields.MoneyField(decimal_places=12, default=0, max_digits=32)),
                ('is_ohlc_price_used', models.BooleanField(default=False)),
                ('ohlc_period', models.IntegerField(default=60, help_text='minutes')),
                ('low_orders_match', models.BooleanField(default=False)),
                ('low_orders_max_match_size', models.FloatField(default=1.0)),
                ('low_orders_spread_size', models.FloatField(default=1.0)),
                ('low_orders_min_order_size', models.FloatField(default=1.0)),
                ('low_orders_match_greater_order', models.BooleanField(default=False)),
                ('low_spread_alert', models.BooleanField(default=False)),
                ('cancel_order_error', models.BooleanField(default=False)),
                ('create_order_error', models.BooleanField(default=False)),
                ('authorization_error', models.BooleanField(default=False)),
                ('binance_api_key', models.CharField(blank=True, default='', max_length=255)),
                ('binance_secret_key', models.CharField(blank=True, default='', max_length=255)),
                ('liquidity_buy_order_size', models.FloatField(default=1.0, help_text='In base currency')),
                ('liquidity_sell_order_size', models.FloatField(default=1.0, help_text='In base currency')),
                ('liquidity_order_step', models.FloatField(default=0.1)),
                ('liquidity_min_btc_balance', lib.fields.MoneyField(decimal_places=12, default=0, max_digits=32)),
                ('liquidity_min_eth_balance', lib.fields.MoneyField(decimal_places=12, default=0, max_digits=32)),
                ('liquidity_min_usdt_balance', lib.fields.MoneyField(decimal_places=12, default=0, max_digits=32)),
                ('ohlc_range_from', models.FloatField(default=1.0)),
                ('ohlc_range_to', models.FloatField(default=1.0)),
                ('ohlc_step', models.FloatField(default=1.0)),
                ('ohlc_HL_delta', models.FloatField(default=1.0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='botconfig',
            index=models.Index(fields=['enabled', 'next_launch'], name='bots_botcon_enabled_48b201_idx'),
        ),
    ]
