# Generated by Django 3.2.13 on 2023-08-06 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_brokerage_alias'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brokerage',
            name='name',
            field=models.CharField(choices=[('interactive_brokers', 'Interactive Brokers'), ('tradezero', 'TradeZero'), ('binance', 'Binance'), ('coinbase', 'Coinbase'), ('kucoin', 'KuCoin'), ('bybit', 'Bybit'), ('okx', 'OKX'), ('bitstamp', 'Bitstamp'), ('bitfinex', 'Bitfinex'), ('gate_io', 'Gate.io'), ('gemini', 'Gemini'), ('bitget', 'Bitget'), ('huobi', 'Huobi'), ('mercado_bitcoin', 'Mercado Bitcoin'), ('foxbit', 'Foxbit')], max_length=20),
        ),
        migrations.AlterField(
            model_name='order',
            name='currency_primary',
            field=models.CharField(max_length=8),
        ),
        migrations.AlterField(
            model_name='order',
            name='open_close',
            field=models.CharField(max_length=5),
        ),
    ]