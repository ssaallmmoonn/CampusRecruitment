from django.db import models
from users.models import Student
from jobs.models import Job

class UserItemScore(models.Model):
    """
    用户-岗位交互聚合评分表
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='学生')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, verbose_name='职位')
    score = models.FloatField(default=0.0, verbose_name='最终分数')
    view_cnt = models.PositiveIntegerField(default=0, verbose_name='浏览次数')
    collect_cnt = models.PositiveIntegerField(default=0, verbose_name='收藏次数')
    deliver_cnt = models.PositiveIntegerField(default=0, verbose_name='投递次数')
    last_action_time = models.DateTimeField(auto_now=True, verbose_name='最后交互时间')

    class Meta:
        verbose_name = '推荐-用户评分聚合'
        verbose_name_plural = verbose_name
        unique_together = ('student', 'job')
        indexes = [
            models.Index(fields=['student', 'job']),
        ]

class ItemSimilarity(models.Model):
    """
    岗位相似度表 (Item-based CF)
    """
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='sim_source', verbose_name='主岗位')
    sim_job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='sim_target', verbose_name='相似岗位')
    similarity = models.FloatField(verbose_name='相似度')
    co_cnt = models.PositiveIntegerField(default=0, verbose_name='共同交互用户数')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '推荐-岗位相似度'
        verbose_name_plural = verbose_name
        unique_together = ('job', 'sim_job')
        indexes = [
            models.Index(fields=['job', '-similarity']),
        ]

class UserSimilarity(models.Model):
    """
    用户相似度表 (User-based CF)
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='user_sim_source', verbose_name='学生')
    sim_student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='user_sim_target', verbose_name='相似学生')
    similarity = models.FloatField(verbose_name='相似度')
    co_cnt = models.PositiveIntegerField(default=0, verbose_name='共同交互岗位数')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '推荐-用户相似度'
        verbose_name_plural = verbose_name
        unique_together = ('student', 'sim_student')
        indexes = [
            models.Index(fields=['student', '-similarity']),
        ]

class Recommendation(models.Model):
    """
    最终推荐结果表 (Hybrid)
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='recommendations', verbose_name='学生')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='recommendations', verbose_name='推荐职位')
    score_item = models.FloatField(default=0.0, verbose_name='Item-based分数')
    score_user = models.FloatField(default=0.0, verbose_name='User-based分数')
    score_hybrid = models.FloatField(default=0.0, verbose_name='混合分数')
    reason = models.JSONField(verbose_name='推荐理由', null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '推荐结果'
        verbose_name_plural = verbose_name
        unique_together = ('student', 'job')
        indexes = [
            models.Index(fields=['student', '-score_hybrid']),
        ]
