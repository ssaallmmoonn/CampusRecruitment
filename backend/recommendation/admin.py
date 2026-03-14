from django.contrib import admin
from .models import UserItemScore, ItemSimilarity, UserSimilarity, Recommendation

@admin.register(UserItemScore)
class UserItemScoreAdmin(admin.ModelAdmin):
    list_display = ('student', 'job', 'score', 'view_cnt', 'collect_cnt', 'deliver_cnt', 'last_action_time')
    search_fields = ('student__name', 'job__job_name')
    list_filter = ('last_action_time',)

@admin.register(ItemSimilarity)
class ItemSimilarityAdmin(admin.ModelAdmin):
    list_display = ('job', 'sim_job', 'similarity', 'co_cnt', 'update_time')
    search_fields = ('job__job_name', 'sim_job__job_name')
    list_filter = ('update_time',)

@admin.register(UserSimilarity)
class UserSimilarityAdmin(admin.ModelAdmin):
    list_display = ('student', 'sim_student', 'similarity', 'co_cnt', 'update_time')
    search_fields = ('student__name', 'sim_student__name')
    list_filter = ('update_time',)

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('student', 'job', 'score_hybrid', 'score_item', 'score_user', 'update_time')
    search_fields = ('student__name', 'job__job_name')
    ordering = ('-score_hybrid',)
    list_filter = ('update_time',)
