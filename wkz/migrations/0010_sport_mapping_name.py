# Generated by Django 3.2.7 on 2021-10-24 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wkz", "0009_auto_20211006_2053"),
    ]

    operations = [
        migrations.AddField(
            model_name="sport",
            name="mapping_name",
            field=models.CharField(blank=True, max_length=24, null=True, unique=True, verbose_name="Mapping Name"),
        ),
    ]