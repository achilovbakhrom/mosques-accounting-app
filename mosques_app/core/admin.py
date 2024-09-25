"""
Django admin customization.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ['id']
    list_display = ['username', 'name', 'place', 'role']
    list_editable = ['username', 'place', 'role']
    list_display_links = None
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal Info'), {'fields': ('name',)}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'password1',
                'password2',
                'role',
                'name',
                'place',
                'is_active',
                'is_staff',
                'is_superuser',
            ),
        }),
    )


admin.site.register(models.User, UserAdmin)

# Unit model

class UnitAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('id', 'name', 'created_at', 'updated_at', 'created_by', 'updated_by')

    list_editable = ('name',)

    list_display_links = None

    # Add a search bar
    search_fields = ('name',)

    # Add filters
    list_filter = ('created_by',)

admin.site.register(models.Unit, UnitAdmin)


class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp', 'object_id', 'object_type', 'description', 'ip_address')

    search_fields = ('user', 'action', 'timestamp', 'object_type', 'object_id', 'description', 'ip_address')

    def has_add_permission(self, request):
        return False

admin.site.register(models.ActivityLog, ActivityLogAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'percentage', 'operation_type', 'unit', 'created_at', 'updated_at', 'created_by', 'updated_by')
    search_fields = ('name', 'operation_type',)

    list_editable = ('name', 'operation_type', 'percentage')

    list_display_links = None

admin.site.register(models.Category, CategoryAdmin)

class PlaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent', 'place_type',)
    search_fields = ('name', 'place_type',)
    list_editable = ('name', 'parent', 'place_type',)
    list_display_links = None

admin.site.register(models.Place, PlaceAdmin)

class RecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'place', 'date', 'category', 'amount', 'created_by', 'quantity', 'unit', 'description')
    search_fields = ('date', 'category', 'amount', 'quantity', 'unit', 'description')

admin.site.register(models.Record, RecordAdmin)