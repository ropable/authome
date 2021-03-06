import logging
import traceback

from django.contrib import admin
from django.utils import timezone
from django.conf import settings
from django.contrib import messages,auth
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import mark_safe
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db.models import Q

from . import models
from . import forms

logger = logging.getLogger(__name__)

class DatetimeMixin(object):
    def _modified(self,obj):
        if not obj or not obj.modified :
            return ""
        else:
            return timezone.localtime(obj.modified).strftime("%Y-%m-%d %H:%M:%S")
    _modified.short_description = "Modified"

    def _created(self,obj):
        if not obj or not obj.created :
            return ""
        else:
            return timezone.localtime(obj.created).strftime("%Y-%m-%d %H:%M:%S")
    _created.short_description = "Created"

    def _last_login(self,obj):
        if not obj or not obj.last_login :
            return ""
        else:
            return timezone.localtime(obj.last_login).strftime("%Y-%m-%d %H:%M:%S")
    _last_login.short_description = "Last Login"

    def _date_joined(self,obj):
        if not obj or not obj.date_joined :
            return ""
        else:
            return timezone.localtime(obj.date_joined).strftime("%Y-%m-%d %H:%M:%S")
    _date_joined.short_description = "Date Joined"

admin.site.unregister(auth.models.Group)

@admin.register(models.User)
class UserAdmin(DatetimeMixin,auth.admin.UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff','usergroup','last_idp','_last_login')
    list_filter = ( 'is_superuser', 'usergroup')
    add_form_template = 'admin/change_form.html'
    add_form = forms.UserCreateForm
    readonly_fields = ("_last_login","_date_joined","username","first_name","last_name","is_staff","_email")
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ("email",)
        }),
    )
    fieldsets = (
        (None, {'fields': ('_email', )}),
        ('Personal info', {'fields': ('username','first_name', 'last_name')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', ),
        }),
        ('Important dates', {'fields': ('_last_login', '_date_joined')}),
    )

    def _email(self,obj):
        if not obj :
            return ""
        else:
            return obj.email
    _email.short_description = "Email"


@admin.register(models.UserGroup)
class UserGroupAdmin(DatetimeMixin,admin.ModelAdmin):
    list_display = ('name','parent_group','users','excluded_users','identity_provider','_modified','_created')
    readonly_fields = ('_modified',)
    fields = ('name','parent_group','users','excluded_users','identity_provider','_modified')
    ordering = ('parent_group','name',)
    form = forms.UserGroupForm

@admin.register(models.UserGroupAuthorization)
class UserGroupAuthorizationAdmin(DatetimeMixin,admin.ModelAdmin):
    list_display = ('usergroup','domain','paths','excluded_paths','_modified','_created')
    readonly_fields = ('_modified',)
    fields = ('usergroup','domain','paths','excluded_paths','_modified')
    ordering = ('usergroup','sortkey',)
    form = forms.UserGroupAuthorizationForm

@admin.register(models.UserAuthorization)
class UserAuthorizationAdmin(DatetimeMixin,admin.ModelAdmin):
    list_display = ('user','domain','paths','excluded_paths','_modified','_created')
    readonly_fields = ('_modified',)
    fields = ('user','domain','paths','excluded_paths','_modified')
    ordering = ('user','sortkey',)
    form = forms.UserAuthorizationForm

class UserAccessToken(models.User):
    class Meta:
        proxy = True
        verbose_name_plural = "  User Access Tokens"

class TokenStatusFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Token Status'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'token_status'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        if settings.USER_ACCESS_TOKEN_WARNING:
            return [("all_token","All Token"),('valid_token','Valid Token'),('soon_expired_token',"Soon Expired Token"),("expired_token","Expired Token")]
        else:
            return [("all_token","All Token"),('valid_token','Valid Token'),("Expired_token","Expired Token")]


    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        val = self.value()
        if not val:
            return queryset
        elif val == 'all_token':
            return queryset.filter(token__isnull=False,token__token__isnull=False)
        elif val == "valid_token":
            return queryset.filter(token__isnull=False,token__enabled=True,token__token__isnull=False).filter(Q(token__expired__isnull=True) | Q(token__expired__gte=timezone.localdate()))
        elif val == "soon_expired_token":
            return queryset.filter(token__isnull=False,token__token__isnull=False,token__expired__gte=timezone.localdate(),token__expired__lt=timezone.localdate() + settings.USER_ACCESS_TOKEN_WARNING)
        elif val == "expired_token":
            return queryset.filter(token__isnull=False,token__token__isnull=False,token__expired__lt=timezone.localdate())
        else:
            return queryset

@admin.register(UserAccessToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ('email','last_name','first_name','is_staff','is_superuser','is_active','_token_enabled','_token_short','_token_created','_token_expired')
    readonly_fields = ('email','last_name','first_name','is_staff','is_superuser','is_active','_token_enabled','_token','_token_created','_token_expired')
    ordering = ('email',)
    actions = ('enable_token','disable_token','generate_token','revoke_token')
    search_fields=("email","last_name","first_name")
    list_filter = (TokenStatusFilter,)

    def _enable_token(self,request, queryset,enable):
        for user in queryset:
            try:
                try:
                    token = models.UserToken.objects.get(user=user)
                    if enable:
                        if token.enabled:
                            self.message_user(request, "{}: The access token was already enabled before".format(user.email))
                        else:
                            token.enabled = True
                            token.save(update_fields=["enabled"])
                            self.message_user(request, "{}: The access token is enabled.".format(user.email))
                    else:
                        if token.enabled:
                            token.enabled = False
                            token.save(update_fields=["enabled"])
                            self.message_user(request, "{}: The access token is disabled.".format(user.email))
                        else:
                            self.message_user(request, "{}: The access token was already disabled before".format(user.email))
                except ObjectDoesNotExist as ex:
                    if enable:
                        models.UserToken(user=user,enabled=True).save()
                        self.message_user(request, "{}: The access token is enabled".format(user.email))
                    else:
                        self.message_user(request, "{}: The access token was never enabled before.".format(user.email))
            except Exception as ex:
                logger.error("{}:Failed to {} the access token..{}".format(user.email,"enable" if enable else "disable",traceback.format_exc()))
                self.message_user(request, "{}:Failed to {} the access token..{}".format(user.email,"enable" if enable else "disable",str(ex)),level=messages.ERROR)

    def enable_token(self,request, queryset):
        self._enable_token(request,queryset,True)
    enable_token.short_description = 'Enable Access Token'

    def disable_token(self,request, queryset):
        self._enable_token(request,queryset,False)
    disable_token.short_description = 'Disable Access Token'

    def generate_token(self,request, queryset):
        token = None
        enable_token = 0
        for user in queryset:
            try:
                enable_token = 0
                #enable the access token if not enabled before
                try:
                    token = models.UserToken.objects.get(user=user)
                    if not token.enabled:
                        token.enabled = True
                        enable_token = 1
                except ObjectDoesNotExist as ex:
                    token = models.UserToken(user=user,enabled=True)
                    enable_token = 2

                token.generate_token()
                if enable_token == 2:
                    token.save()
                    self.message_user(request, "{}: Succeed to enable and generate the access token".format(user.email))
                elif enable_token == 1:
                    token.save(update_fields=["enabled","token","created","expired"])
                    self.message_user(request, "{}: Succeed to enable and generate the access token".format(user.email))
                else:
                    token.save(update_fields=["token","created","expired"])
                    self.message_user(request, "{}: Succeed to generate the access token".format(user.email))

            except Exception as ex:
                logger.error("{}:Failed to generate access token..{}".format(user.email,traceback.format_exc()))
                self.message_user(request, "{}:Failed to generate access token..{}".format(user.email,str(ex)),level=messages.ERROR)
    generate_token.short_description = 'Generate Access Token'

    def revoke_token(self,request, queryset):
        token = None
        for user in queryset:
            try:
                #enable the access token if not enabled before
                try:
                    token = models.UserToken.objects.get(user=user)
                    if not token.token:
                        self.message_user(request, "{}: Has no access token".format(user.email))
                    else:
                        token.token = None
                        token.created = None
                        token.expired = None
                        token.save(update_fields=["token","created","expired"])
                        self.message_user(request, "{}:Succeed to revoke the access token".format(user.email))

                except ObjectDoesNotExist as ex:
                    self.message_user(request, "{}: Has no access token".format(user.email))
            except Exception as ex:
                logger.error("{}:Failed to revoke access token..{}".format(user.email,traceback.format_exc()))
                self.message_user(request, "{}:Failed to revoke access token..{}".format(user.email,str(ex)),level=messages.ERROR)
    revoke_token.short_description = 'Revoke Access Token'

    def _token_enabled(self,obj):
        if not obj or not obj.token:
            return False
        else:
            return obj.token.enabled
    _token_enabled.boolean = True
    _token_enabled.short_description = "Token Enabled"

    def _token(self,obj):
        if not obj or not obj.token or not obj.token.token:
            return None
        else:
            return obj.token.token
    _token.short_description = "Token"

    def _token_short(self,obj):
        if not obj or not obj.token or not obj.token.token:
            return None
        else:
            return obj.token.token
    _token_short.short_description = "Token"

    def _token_created(self,obj):
        if not obj or not obj.token or not obj.token.token or not obj.token.created:
            return None
        else:
            return timezone.localtime(obj.token.created).strftime("%Y-%m-%d %H:%M:%S")
    _token_created.short_description = "Token Created At"

    def _token_expired(self,obj):
        if not obj or not obj.token or not obj.token.token:
            return None
        elif not obj.token.expired:
            return mark_safe("<A style='background-color:green;color:white;padding:0px 20px 0px 20px;'>2099-12-31</A>")
        else:
            t = obj.token.expired.strftime("%Y-%m-%d")
            status = obj.token.status
            if status < 0:
                return mark_safe("<A style='background-color:darkred;color:white;padding:0px 20px 0px 20px;'>{}</A>".format(t))
            elif status == models.UserToken.GOOD:
                return mark_safe("<A style='background-color:green;color:white;padding:0px 20px 0px 20px;'>{}</A>".format(t))
            else:
                return mark_safe("<A style='background-color:#ff9966;color:white;padding:0px 20px 0px 20px;'>{}</A>".format(t))
    _token_expired.short_description = "Token Expired At"


    def _token_is_expired(self,obj):
        if not obj or not obj.token or not obj.token.token:
            return None
        else:
            return mark_safe("<img src='{}'/>".format(static('admin/img/icon-%s.svg' % {True: 'yes', False: 'no'}[obj.token.is_expired])))
    _token_is_expired.short_description = "Token Expired"


    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(models.IdentityProvider)
class IdentityProviderAdmin(DatetimeMixin,admin.ModelAdmin):
    list_display = ('idp','name','userflow','logout_url','domains','_modified','_created')
    readonly_fields = ('idp','_modified','_created')
    form = forms.IdentityProviderForm
    fields = ('idp','name','userflow','logout_url','domains','_modified','_created')
    ordering = ('name','idp',)

