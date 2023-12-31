# Generated by Django 3.2.13 on 2023-08-08 08:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0012_auto_20230807_2213'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=10)),
                ('long_short', models.CharField(max_length=5)),
                ('win_loss', models.CharField(max_length=5)),
                ('quantity_of_orders', models.IntegerField()),
                ('quantity_trade_asset', models.FloatField()),
                ('trade_money', models.FloatField()),
                ('trade_result', models.FloatField()),
                ('trade_result_percentage', models.FloatField()),
                ('trade_brokerage_commission', models.FloatField()),
                ('date_open', models.DateTimeField()),
                ('date_close', models.DateTimeField()),
                ('holding_time', models.CharField(max_length=20)),
            ],
            options={
                'ordering': ['-date_close'],
            },
        ),
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['-date_time']},
        ),
        migrations.AddField(
            model_name='order',
            name='processed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='order',
            name='brokerage_commission',
            field=models.FloatField(default=0.0, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='buy_sell',
            field=models.CharField(choices=[('buy', 'buy'), ('sell', 'sell')], max_length=5),
        ),
        migrations.AlterField(
            model_name='order',
            name='open_close',
            field=models.CharField(choices=[('open', 'open'), ('close', 'close'), ('flip', 'flip')], max_length=5),
        ),
        migrations.AddField(
            model_name='order',
            name='trade',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='base.trade'),
        ),
    ]
