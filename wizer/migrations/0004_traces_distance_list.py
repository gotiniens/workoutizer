# Generated by Django 3.0.8 on 2020-08-01 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wizer', '0003_auto_20200709_0742'),
    ]

    operations = [
        migrations.AddField(
            model_name='traces',
            name='distance_list',
            field=models.CharField(default='[]', max_length=10000000000),
        ),
    ]