# Generated by Django 3.1.6 on 2022-02-21 00:27

import authome.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authome', '0025_auto_20210622_0805'),
    ]

    operations = [
        migrations.AddField(
            model_name='usergroup',
            name='session_timeout',
            field=models.PositiveSmallIntegerField(blank=True, help_text='Session timeout in seconds, 0 means never timeout', null=True),
        ),
        migrations.AlterField(
            model_name='customizableuserflow',
            name='domain',
            field=models.CharField(help_text='\nA domain or domain pattern\nThe following lists all valid options in the checking order\n    1. Single Domain  : Represent a single domain. For example oim.dbca.wa.gov.au.\n    2. Domain Pattern : A domain pattern, \'*" represents any strings. For example  pbs*dbca.wa.gov.au\n    3. Domain Regex   : A regex string starts with \'^\'. For example  ^pbs[^\\.]*\\.dbca\\.wa\\.gov\\.au$\n    4. Suffix Domain  : A string Starts with \'.\' followed by a domain. For example .dbca.wa.gov.au\n    5. All Domain     : \'*\'\n', max_length=128),
        ),
        migrations.AlterField(
            model_name='userauthorization',
            name='domain',
            field=models.CharField(help_text='\nA domain or domain pattern\nThe following lists all valid options in the checking order\n    1. Single Domain  : Represent a single domain. For example oim.dbca.wa.gov.au.\n    2. Domain Pattern : A domain pattern, \'*" represents any strings. For example  pbs*dbca.wa.gov.au\n    3. Domain Regex   : A regex string starts with \'^\'. For example  ^pbs[^\\.]*\\.dbca\\.wa\\.gov\\.au$\n    4. Suffix Domain  : A string Starts with \'.\' followed by a domain. For example .dbca.wa.gov.au\n    5. All Domain     : \'*\'\n', max_length=128),
        ),
        migrations.AlterField(
            model_name='usergroup',
            name='excluded_users',
            field=authome.models.ArrayField(base_field=models.CharField(max_length=64), blank=True, help_text="\nList all possible user emails in this group separated by new line character.\nThe following lists all valid options in the checking order\n    1. All Emails    : *\n    2. Domain Email  : Starts with '@', followed by email domain. For example@dbca.wa.gov.au\n    3. Email Pattern : A email pattern,'*' represents any strings. For example test_*@dbca.wa.gov.au\n    4. User Email    : A single user email, For example test_user01@dbca.wa.gov.au\n", null=True, size=None),
        ),
        migrations.AlterField(
            model_name='usergroup',
            name='users',
            field=authome.models.ArrayField(base_field=models.CharField(max_length=64), help_text="\nList all possible user emails in this group separated by new line character.\nThe following lists all valid options in the checking order\n    1. All Emails    : *\n    2. Domain Email  : Starts with '@', followed by email domain. For example@dbca.wa.gov.au\n    3. Email Pattern : A email pattern,'*' represents any strings. For example test_*@dbca.wa.gov.au\n    4. User Email    : A single user email, For example test_user01@dbca.wa.gov.au\n", size=None),
        ),
        migrations.AlterField(
            model_name='usergroupauthorization',
            name='domain',
            field=models.CharField(help_text='\nA domain or domain pattern\nThe following lists all valid options in the checking order\n    1. Single Domain  : Represent a single domain. For example oim.dbca.wa.gov.au.\n    2. Domain Pattern : A domain pattern, \'*" represents any strings. For example  pbs*dbca.wa.gov.au\n    3. Domain Regex   : A regex string starts with \'^\'. For example  ^pbs[^\\.]*\\.dbca\\.wa\\.gov\\.au$\n    4. Suffix Domain  : A string Starts with \'.\' followed by a domain. For example .dbca.wa.gov.au\n    5. All Domain     : \'*\'\n', max_length=128),
        ),
    ]
