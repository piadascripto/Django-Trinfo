# Generated by Django 3.2.13 on 2023-08-03 18:11

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0007_alter_orders_brokerage'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Brokerages',
            new_name='Brokerage',
        ),
        migrations.RenameModel(
            old_name='Orders',
            new_name='Order',
        ),
        migrations.RenameModel(
            old_name='Tags',
            new_name='Tag',
        ),
    ]
