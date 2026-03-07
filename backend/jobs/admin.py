from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('job_name', 'company', 'salary', 'location', 'audit_status', 'create_time')
    list_filter = ('audit_status', 'create_time')
    search_fields = ('job_name', 'company__company_name')
    actions = ['approve_job', 'reject_job']

    @admin.action(description='通过审核')
    def approve_job(self, request, queryset):
        queryset.update(audit_status=1)

    @admin.action(description='驳回审核')
    def reject_job(self, request, queryset):
        queryset.update(audit_status=2)
