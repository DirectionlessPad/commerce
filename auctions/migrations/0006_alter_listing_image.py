# Generated by Django 4.2.10 on 2024-02-09 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_alter_listing_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='image',
            field=models.URLField(max_length=512, null=True),
        ),
    ]
