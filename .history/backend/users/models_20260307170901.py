from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom User model.
    Inherits from AbstractUser which provides:
    username, password, first_name, last_name, email, is_staff, is_active, date_joined
    """
    ROLE_CHOICES = (
        (1, 'Student'),
        (2, 'Company'),
        (3, 'Administrator'),
    )
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=1, verbose_name='角色')
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='student_profile', verbose_name='关联用户')
    name = models.CharField(max_length=20, verbose_name='姓名')
    major = models.CharField(max_length=50, verbose_name='专业')
    education = models.CharField(max_length=20, verbose_name='学历')
    graduation_year = models.IntegerField(null=True, blank=True, verbose_name='毕业年份')

    def __str__(self):
        return self.name if self.name else self.user.username

    class Meta:
        verbose_name = '学生信息'
        verbose_name_plural = verbose_name

class Company(models.Model):
    AUDIT_STATUS_CHOICES = (
        (0, '待审核'),
        (1, '通过'),
        (2, '驳回'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='company_profile', verbose_name='关联用户')
    company_name = models.CharField(max_length=100, verbose_name='企业名称')
    credit_code = models.CharField(max_length=50, verbose_name='统一社会信用代码')
    audit_status = models.PositiveSmallIntegerField(choices=AUDIT_STATUS_CHOICES, default=0, verbose_name='审核状态')
    contact_person = models.CharField(max_length=20, blank=True, verbose_name='联系人')
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name='联系电话')
    description = models.TextField(blank=True, verbose_name='企业简介')
    address = models.CharField(max_length=200, blank=True, verbose_name='办公地点')

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = '企业信息'
        verbose_name_plural = verbose_name
