from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Student, Company

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'major', 'education', 'graduation_year')
    search_fields = ('name', 'major', 'user__username')

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'audit_status', 'contact_person', 'contact_phone')
    list_filter = ('audit_status',)
    search_fields = ('company_name', 'user__username')
    actions = ['approve_company', 'reject_company']

    @admin.action(description='通过审核')
    def approve_company(self, request, queryset):
        queryset.update(audit_status=1)

    @admin.action(description='驳回审核')
    def reject_company(self, request, queryset):
        queryset.update(audit_status=2)
