# Generated by Django 4.2.10 on 2024-02-09 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_listing_name_alter_listing_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listing',
            old_name='name',
            new_name='title',
        ),
        migrations.AddField(
            model_name='listing',
            name='category',
            field=models.CharField(choices=[('DE', 'default'), ('FD', 'Food and Drink')], max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='listing',
            name='description',
            field=models.CharField(max_length=1500, null=True),
        ),
        migrations.AddField(
            model_name='listing',
            name='image',
            field=models.URLField(null=True),
        ),
        migrations.AddField(
            model_name='listing',
            name='starting_bid',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='listing',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
