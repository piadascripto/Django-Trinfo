# Generated by Django 3.2.13 on 2023-08-03 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_alter_orders_brokerage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='brokerage',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
