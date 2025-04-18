# Generated by Django 5.1.1 on 2025-04-10 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='min_delivery_time',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='offer',
            name='min_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
