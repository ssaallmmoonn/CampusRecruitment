from django.db import models
from users.models import Company

class Job(models.Model):
    AUDIT_STATUS_CHOICES = (
        (0, '待审核'),
        (1, '通过'),
        (2, '驳回'),
        (3, '下架'),
    )

    DEGREE_CHOICES = (
        ('初中及以下', '初中及以下'),
        ('高中', '高中'),
        ('中专/中技', '中专/中技'),
        ('大专', '大专'),
        ('本科', '本科'),
        ('硕士', '硕士'),
        ('博士', '博士'),
        ('学历不限', '学历不限'),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs', verbose_name='发布企业', null=True)
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

    # New fields for UI
    job_type = models.CharField(max_length=20, default='全职', verbose_name='工作性质')  # 全职/实习
    degree_requirement = models.CharField(max_length=20, choices=DEGREE_CHOICES, default='本科', verbose_name='学历要求')
    experience_requirement = models.CharField(max_length=20, default='不限', verbose_name='经验要求')  # 无经验/1-3年/不限
    
    # New fields for Filter
    # Temporary rename to avoid conflicts, then we will rename back or migrate properly
    job_category = models.ForeignKey('JobCategory', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='职位分类', db_column='job_category_link_id')
    major = models.ForeignKey('MajorCategory', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='专业分类', db_column='major_link_id')
    
    # Deprecated fields (will be removed later)
    # job_category = models.CharField(max_length=50, blank=True, verbose_name='职位分类(旧)', db_column='job_category_id')
    # major = models.CharField(max_length=50, blank=True, verbose_name='专业分类(旧)')
    
    major_requirement = models.CharField(max_length=50, blank=True, verbose_name='专业要求') # Legacy, or text description
    search_keywords = models.JSONField(default=list, blank=True, verbose_name='搜索关键词')
    reject_reason = models.CharField(max_length=200, blank=True, null=True, verbose_name='驳回原因')

    def __str__(self):
        return self.job_name

    class Meta:
        verbose_name = '职位'
        verbose_name_plural = verbose_name

class JobCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name='名称')
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE, verbose_name='父级')
    level = models.PositiveSmallIntegerField(verbose_name='层级')
    path = models.CharField(max_length=255, unique=True, verbose_name='路径')

    def save(self, *args, **kwargs):
        if not self.path:
            if self.parent_id:
                self.path = f'{self.parent.path}/{self.name}'
            else:
                self.path = self.name
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = '职位分类'
        verbose_name_plural = verbose_name
        unique_together = ('parent', 'name')

    def __str__(self):
        return self.path

class MajorCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name='名称')
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE, verbose_name='父级')
    level = models.PositiveSmallIntegerField(verbose_name='层级')
    path = models.CharField(max_length=255, unique=True, verbose_name='路径')

    def save(self, *args, **kwargs):
        if not self.path:
            if self.parent_id:
                self.path = f'{self.parent.path}/{self.name}'
            else:
                self.path = self.name
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = '专业分类'
        verbose_name_plural = verbose_name
        unique_together = ('parent', 'name')

    def __str__(self):
        return self.path
