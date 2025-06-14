from django.contrib import admin
from userauths import models
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from userauths.models import User, Profile

class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'username', 'date_joined', 'is_staff')
    search_fields = ('email', 'username')
    ordering = ('-date_joined',)

admin.site.register(User, UserAdmin)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'get_email', 'mobile')
    search_fields = ('user__email', 'full_name', 'mobile')

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

    def get_full_name(self, obj):
        return obj.full_name or obj.user.username
    get_full_name.short_description = 'Full Name'

admin.site.register(Profile, ProfileAdmin)