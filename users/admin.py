from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = [
        "email",
        "username",
        "name",
        "is_admin",
        "is_super_admin",
        "is_verified",
    ]
    fieldsets = UserAdmin.fieldsets + (
        (
            None,
            {
                "fields": (
                    "name",
                    "is_admin",
                    "is_super_admin",
                    "is_verified",
                )
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("name", "is_admin", "is_super_admin", "is_verified")}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
