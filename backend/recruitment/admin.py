from django.contrib import admin
from .models import Resume, Behavior, JobApplication

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('student', 'resume_name', 'create_time')
    search_fields = ('student__name', 'resume_name')

@admin.register(Behavior)
class BehaviorAdmin(admin.ModelAdmin):
    list_display = ('student', 'job', 'behavior_type', 'create_time')
    list_filter = ('behavior_type', 'create_time')

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'job', 'status', 'create_time')
    list_filter = ('status', 'create_time')
    search_fields = ('student__name', 'job__job_name')
