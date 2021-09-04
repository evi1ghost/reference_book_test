from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Employee, Organization, Phone, User


admin.site.register(User, UserAdmin)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'name', 'address', 'description', 'owner'
    )
    raw_id_fields = ('modifiers',)
    search_fields = ('name',)
    list_filter = ('modifiers',)
    empty_value_display = '-пусто-'

    fieldsets = (
        (None, {
            'fields': (
                'name', 'address', 'description', 'owner', 'modifiers'
            ),
        }),
    )


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'name', 'position', 'organization'
    )
    search_fields = ('name',)
    list_filter = ('organization',)
    empty_value_display = '-пусто-'


@admin.register(Phone)
class PhoneAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'phone_number', 'phone_type', 'employee'
    )
    search_fields = ('phone_number',)
    list_filter = ('phone_type',)
    empty_value_display = '-пусто-'
