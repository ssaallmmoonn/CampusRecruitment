from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom User model.
    Inherits from AbstractUser which provides:
    username, password, first_name, last_name, email, is_staff, is_active, date_joined
    """
    ROLE_CHOICES = (
        (0, 'Administrator'), # Ensure Admin is 0
        (1, 'Student'),
        (2, 'Company'),
    )
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=1, verbose_name='角色')
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

class Student(models.Model):
    DEGREE_CHOICES = (
        ('初中及以下', '初中及以下'),
        ('高中', '高中'),
        ('中专/中技', '中专/中技'),
        ('大专', '大专'),
        ('本科', '本科'),
        ('硕士', '硕士'),
        ('博士', '博士'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='student_profile', verbose_name='关联用户')
    name = models.CharField(max_length=20, verbose_name='姓名')
    major = models.CharField(max_length=50, verbose_name='专业')
    school = models.CharField(max_length=50, verbose_name='学校', blank=True)
    education = models.CharField(max_length=20, choices=DEGREE_CHOICES, verbose_name='学历')
    graduation_year = models.IntegerField(null=True, blank=True, verbose_name='毕业年份')
    
    # New fields
    phone = models.CharField(max_length=20, blank=True, verbose_name='电话号码')
    email = models.EmailField(blank=True, verbose_name='邮箱', null=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='头像')
    job_intention = models.CharField(max_length=50, blank=True, verbose_name='求职意向')

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
    reject_reason = models.CharField(max_length=200, blank=True, verbose_name='驳回原因')
    contact_person = models.CharField(max_length=20, blank=True, verbose_name='联系人')
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name='联系电话')
    description = models.TextField(blank=True, verbose_name='企业简介')
    address = models.CharField(max_length=200, blank=True, verbose_name='办公地点')
    
    # New fields for UI
    logo = models.ImageField(upload_to='company_logos/', max_length=255, blank=True, null=True, verbose_name='企业Logo')
    industry = models.CharField(max_length=50, blank=True, verbose_name='所属行业')
    scale = models.CharField(max_length=50, blank=True, verbose_name='人员规模')
    nature = models.CharField(max_length=50, blank=True, verbose_name='企业性质')
    # financing_stage removed (merged/deleted as requested)

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = '企业信息'
        verbose_name_plural = verbose_name

class Administrator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='admin_profile', verbose_name='关联用户')
    name = models.CharField(max_length=50, verbose_name='姓名')
    avatar = models.ImageField(upload_to='admin_avatars/', null=True, blank=True, verbose_name='头像')
    phone = models.CharField(max_length=20, blank=True, verbose_name='电话')
    email = models.EmailField(blank=True, null=True, verbose_name='邮箱')

    def __str__(self):
        return self.name if self.name else self.user.username

    class Meta:
        verbose_name = '管理员信息'
        verbose_name_plural = verbose_name

class Industry(models.Model):
    name = models.CharField(max_length=50, verbose_name='行业名称')
    description = models.TextField(blank=True, verbose_name='行业描述')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '行业信息'
        verbose_name_plural = verbose_name
