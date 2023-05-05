# Generated by Django 3.2.12 on 2022-06-13 02:02

import authome.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authome', '0032_alter_usergroup_identity_provider'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserAccessToken',
        ),
        migrations.CreateModel(
            name='NormalUser',
            fields=[
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': '        Users',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('authome.user',),
        ),
        migrations.CreateModel(
            name='NormalUserToken',
            fields=[
            ],
            options={
                'verbose_name': 'System User',
                'verbose_name_plural': '       User Tokens',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('authome.user',),
        ),
        migrations.CreateModel(
            name='SystemUserToken',
            fields=[
            ],
            options={
                'verbose_name': 'System User',
                'verbose_name_plural': '     System User Tokens',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('authome.user',),
        ),
        migrations.AlterModelOptions(
            name='customizableuserflow',
            options={'verbose_name_plural': '  Customizable userflows'},
        ),
        migrations.AlterModelOptions(
            name='identityprovider',
            options={'verbose_name_plural': '  Identity Providers'},
        ),
        migrations.AlterModelOptions(
            name='systemuser',
            options={'verbose_name': 'System User', 'verbose_name_plural': '      System Users'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'user', 'verbose_name_plural': '        Users'},
        ),
        migrations.AlterModelOptions(
            name='userauthorization',
            options={'verbose_name_plural': ' User Authorizations'},
        ),
        migrations.AlterModelOptions(
            name='usergroup',
            options={'verbose_name_plural': '    User Groups'},
        ),
        migrations.AlterModelOptions(
            name='usertoken',
            options={'verbose_name_plural': ' Access Tokens'},
        ),
        migrations.AlterModelOptions(
            name='usertotp',
            options={'verbose_name_plural': 'User totps'},
        ),
        migrations.AlterField(
            model_name='userauthorization',
            name='paths',
            field=authome.models._ArrayField(base_field=models.CharField(max_length=512), blank=True, help_text="\nList all possible paths separated by new line character.\nThe following lists all valid options in the checking order\n    1. All path      : *\n    2. Prefix path   : the paths except All path, regex path and exact path. For example /admin\n    3. Regex path    : A regex string starts with '^'. For example ^.*/add$\n    4. Exact path  : Starts with '=', represents a single request path . For example =/register\n", null=True, size=None),
        ),
        migrations.AlterField(
            model_name='usergroupauthorization',
            name='paths',
            field=authome.models._ArrayField(base_field=models.CharField(max_length=512), blank=True, help_text="\nList all possible paths separated by new line character.\nThe following lists all valid options in the checking order\n    1. All path      : *\n    2. Prefix path   : the paths except All path, regex path and exact path. For example /admin\n    3. Regex path    : A regex string starts with '^'. For example ^.*/add$\n    4. Exact path  : Starts with '=', represents a single request path . For example =/register\n", null=True, size=None),
        ),
    ]
