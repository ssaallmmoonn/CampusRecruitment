from django.db import models
from users.models import Company

class Job(models.Model):
    AUDIT_STATUS_CHOICES = (
        (0, '待审核'),
        (1, '通过'),
        (2, '驳回'),
        (3, '下架'),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs', verbose_name='发布企业')
    job_name = models.CharField(max_length=50, verbose_name='职位名称')
    salary = models.CharField(max_length=20, verbose_name='薪资')
    location = models.CharField(max_length=50, verbose_name='工作地点')
    description = models.TextField(verbose_name='职位描述')
    requirements = models.TextField(verbose_name='任职要求')
    audit_status = models.PositiveSmallIntegerField(choices=AUDIT_STATUS_CHOICES, default=0, verbose_name='审核状态')
    views_count = models.PositiveIntegerField(default=0, verbose_name='浏览量')
    collections_count = models.PositiveIntegerField(default=0, verbose_name='收藏量')
    deliveries_count = models.PositiveIntegerField(default=0, verbose_name='投递量')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='发布时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.job_name

    class Meta:
        verbose_name = '职位'
        verbose_name_plural = verbose_name
