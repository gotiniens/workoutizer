# Generated by Django 2.2.5 on 2020-01-22 07:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wizer', '0048_auto_20200112_2021'),
    ]

    operations = [
        migrations.AddField(
            model_name='traces',
            name='calories',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]