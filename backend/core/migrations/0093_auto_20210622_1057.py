# Generated by Django 2.2.16 on 2021-06-22 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0092_auto_20210222_0918'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceprovider',
            name='branch_code',
            field=models.CharField(blank=True, max_length=128, verbose_name='branchekode'),
        ),
        migrations.AddField(
            model_name='serviceprovider',
            name='status',
            field=models.CharField(blank=True, max_length=128, verbose_name='status'),
        ),
        migrations.AddField(
            model_name='serviceprovider',
            name='street',
            field=models.CharField(blank=True, max_length=128, verbose_name='vejnavn'),
        ),
        migrations.AddField(
            model_name='serviceprovider',
            name='street_number',
            field=models.CharField(blank=True, max_length=128, verbose_name='vejnummer'),
        ),
        migrations.AddField(
            model_name='serviceprovider',
            name='zip_code',
            field=models.CharField(blank=True, max_length=128, verbose_name='postnummer'),
        ),
    ]
