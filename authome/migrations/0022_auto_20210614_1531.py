# Generated by Django 3.1.6 on 2021-06-14 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authome', '0021_auto_20210614_1518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usergroup',
            name='groupid',
            field=models.SlugField(max_length=8, null=True),
        ),
    ]
