# Generated by Django 2.2.1 on 2019-05-26 20:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wizer', '0008_auto_20190526_2047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sport',
            name='sports_name_slug',
            field=models.CharField(editable=False, max_length=24, unique=True),
        ),
    ]
