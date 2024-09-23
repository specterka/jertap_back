from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User, PasswordResetConfirmation, TwoFactorVerificationOTP, Collaborator


# Register your models here.

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (('Personal info'), {'fields': ('username', 'mobile_number', 'profile_image')}),
        (('Permissions'), {'fields': (
            'is_active', 'is_staff', 'is_superuser', 'is_cafe_owner', 'is_visitor', 'is_cafe_manager'
        )}),
        (('Important dates'), {'fields': ('created_at', 'modified_at',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'mobile_number', 'password1', 'password2')}
         ),
    )

    list_display = (
        'email', 'username', 'auth_provider', 'mobile_number', 'is_cafe_owner', 'is_superuser',
    )
    search_fields = ('email', 'username', 'mobile_number',)
    readonly_fields = ('created_at', 'modified_at',)


admin.site.register(User, CustomUserAdmin)
admin.site.register(PasswordResetConfirmation)
admin.site.register(TwoFactorVerificationOTP)
admin.site.register(Collaborator)
