from django.contrib import admin
from .models import Recommendation

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('student', 'job', 'score', 'create_time')
    search_fields = ('student__name', 'job__job_name')
    ordering = ('-score',)
