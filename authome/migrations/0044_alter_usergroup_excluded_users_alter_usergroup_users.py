# Generated by Django 4.2.13 on 2024-05-14 07:01

import authome.models.models
from authome.models import ArrayField
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authome', '0043_auto_20230511_0924'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usergroup',
            name='excluded_users',
            field=ArrayField(base_field=models.CharField(max_length=64), blank=True, help_text="\nList all possible user emails in this group separated by new line character.\nThe following lists all valid options in the checking order\n    1. All Emails    : *\n    2. Domain Email  : Starts with '@', followed by email domain. For example@dbca.wa.gov.au\n    3. Email Pattern : A email pattern,'*' represents any strings. For example test_*@dbca.wa.gov.au\n    4. Regex Email   : A regex email, starts with '^' and ends with '$'\n    5. User Email    : A single user email, For example test_user01@dbca.wa.gov.au\n", null=True, size=None),
        ),
        migrations.AlterField(
            model_name='usergroup',
            name='users',
            field=ArrayField(base_field=models.CharField(max_length=64), help_text="\nList all possible user emails in this group separated by new line character.\nThe following lists all valid options in the checking order\n    1. All Emails    : *\n    2. Domain Email  : Starts with '@', followed by email domain. For example@dbca.wa.gov.au\n    3. Email Pattern : A email pattern,'*' represents any strings. For example test_*@dbca.wa.gov.au\n    4. Regex Email   : A regex email, starts with '^' and ends with '$'\n    5. User Email    : A single user email, For example test_user01@dbca.wa.gov.au\n", size=None),
        ),
    ]
