# Generated by Django 2.2.16 on 2020-12-01 05:36

import authome.models
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': '      User',
                'db_table': 'auth_user',
                'abstract': False,
                'swappable': 'AUTH_USER_MODEL',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='IdentityProvider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, null=True, unique=True)),
                ('idp', models.CharField(editable=False, max_length=256, unique=True)),
                ('userflow', models.CharField(blank=True, max_length=64, null=True)),
                ('logout_url', models.CharField(blank=True, max_length=512, null=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': ' Identity Providers',
            },
        ),
        migrations.CreateModel(
            name='UserGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True)),
                ('users', authome.models._ArrayField(base_field=models.CharField(max_length=64), help_text="\nList all possible user emails in this group separated by new line character.\nThe following lists all valid options in the checking order\n    1. All emails    : *\n    2. Domain emails : starts with '@', followed by email domain. For example@dbca.wa.gov.au\n    3. Email pattern : '*' represents any strings. For example test_*@dbca.wa.gov.au\n    4. User email    : represent a single user email, For example test_user01@dbca.wa.gov.au\n", size=None)),
                ('excluded_users', authome.models._ArrayField(base_field=models.CharField(max_length=64), blank=True, help_text="\nList all possible user emails in this group separated by new line character.\nThe following lists all valid options in the checking order\n    1. All emails    : *\n    2. Domain emails : starts with '@', followed by email domain. For example@dbca.wa.gov.au\n    3. Email pattern : '*' represents any strings. For example test_*@dbca.wa.gov.au\n    4. User email    : represent a single user email, For example test_user01@dbca.wa.gov.au\n", null=True, size=None)),
                ('modified', models.DateTimeField(db_index=True, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('identity_provider', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='authome.IdentityProvider')),
                ('parent_group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='authome.UserGroup')),
            ],
            options={
                'verbose_name_plural': '     User Groups',
                'unique_together': {('users', 'excluded_users')},
            },
            bases=(authome.models.DbObjectMixin, models.Model),
        ),
        migrations.CreateModel(
            name='UserToken',
            fields=[
                ('user', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='token', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('enabled', models.BooleanField(default=False, editable=False)),
                ('token', models.CharField(editable=False, max_length=128, null=True)),
                ('created', models.DateTimeField(editable=False, null=True)),
                ('expired', models.DateField(editable=False, null=True)),
                ('modified', models.DateTimeField(auto_now=True, db_index=True)),
            ],
            options={
                'verbose_name_plural': '  User Access Tokens',
            },
        ),
        migrations.CreateModel(
            name='UserAuthorization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(help_text='\nA domain or domain pattern \nThe following lists all valid options in the checking order\n    1. Single Domain : Represent a single domain. For example oim.dbca.wa.gov.au. Only single domain can config path and excluded path\n    2. Regex Domain  : \'*" represents any strings. For example  pbs*dbca.wa.gov.au\n    3. Suffix Domain : Starts with \'.\' followed by a domain. For example .dbca.wa.gov.au\n    4. All Domain    : \'*\'\n', max_length=64)),
                ('paths', authome.models._ArrayField(base_field=models.CharField(max_length=128), blank=True, help_text="\nList all possible paths separated by new line character.\nThe following lists all valid options in the checking order\n    1. All path      : *\n    2. Prefix path   : the paths except All path, regex path and exact path. For example /admin\n    3. Regex path    : A regex string starts with '^'. For example ^.*/add$\n    4. Exact path  : Starts with '=', represents a single request path . For example =/register\n", null=True, size=None)),
                ('excluded_paths', authome.models._ArrayField(base_field=models.CharField(max_length=128), blank=True, help_text="\nList all possible paths separated by new line character.\nThe following lists all valid options in the checking order\n    1. All path      : *\n    2. Prefix path   : the paths except All path, regex path and exact path. For example /admin\n    3. Regex path    : A regex string starts with '^'. For example ^.*/add$\n    4. Exact path  : Starts with '=', represents a single request path . For example =/register\n", null=True, size=None)),
                ('sortkey', models.CharField(editable=False, max_length=96)),
                ('modified', models.DateTimeField(db_index=True, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.EmailField(max_length=64)),
            ],
            options={
                'verbose_name_plural': '    User Authorizations',
                'unique_together': {('user', 'domain')},
            },
            bases=(authome.models.DbObjectMixin, models.Model),
        ),
        migrations.AddField(
            model_name='user',
            name='last_idp',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='authome.IdentityProvider'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
        migrations.AddField(
            model_name='user',
            name='usergroup',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, to='authome.UserGroup'),
        ),
        migrations.CreateModel(
            name='UserAccessToken',
            fields=[
            ],
            options={
                'verbose_name_plural': '  User Access Tokens',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('authome.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='UserGroupAuthorization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(help_text='\nA domain or domain pattern \nThe following lists all valid options in the checking order\n    1. Single Domain : Represent a single domain. For example oim.dbca.wa.gov.au. Only single domain can config path and excluded path\n    2. Regex Domain  : \'*" represents any strings. For example  pbs*dbca.wa.gov.au\n    3. Suffix Domain : Starts with \'.\' followed by a domain. For example .dbca.wa.gov.au\n    4. All Domain    : \'*\'\n', max_length=64)),
                ('paths', authome.models._ArrayField(base_field=models.CharField(max_length=128), blank=True, help_text="\nList all possible paths separated by new line character.\nThe following lists all valid options in the checking order\n    1. All path      : *\n    2. Prefix path   : the paths except All path, regex path and exact path. For example /admin\n    3. Regex path    : A regex string starts with '^'. For example ^.*/add$\n    4. Exact path  : Starts with '=', represents a single request path . For example =/register\n", null=True, size=None)),
                ('excluded_paths', authome.models._ArrayField(base_field=models.CharField(max_length=128), blank=True, help_text="\nList all possible paths separated by new line character.\nThe following lists all valid options in the checking order\n    1. All path      : *\n    2. Prefix path   : the paths except All path, regex path and exact path. For example /admin\n    3. Regex path    : A regex string starts with '^'. For example ^.*/add$\n    4. Exact path  : Starts with '=', represents a single request path . For example =/register\n", null=True, size=None)),
                ('sortkey', models.CharField(editable=False, max_length=96)),
                ('modified', models.DateTimeField(db_index=True, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('usergroup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authome.UserGroup')),
            ],
            options={
                'verbose_name_plural': '   User Group Authorizations',
                'unique_together': {('usergroup', 'domain')},
            },
            bases=(authome.models.DbObjectMixin, models.Model),
        ),
        migrations.AlterUniqueTogether(
            name='user',
            unique_together={('email',)},
        ),
    ]
