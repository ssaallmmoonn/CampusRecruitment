from django.db import models
from users.models import Student
from jobs.models import Job

class Resume(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='resumes', verbose_name='所属学生', null=True)
    resume_name = models.CharField(max_length=50, verbose_name='简历名称')
    content = models.JSONField(verbose_name='简历内容') # Store as JSON: basic info, projects, skills, etc.
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return f"{self.student.name} - {self.resume_name}"

    class Meta:
        verbose_name = '简历'
        verbose_name_plural = verbose_name

class Behavior(models.Model):
    BEHAVIOR_TYPE_CHOICES = (
        (1, '浏览'),
        (2, '收藏'),
        (3, '投递'),
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='学生', null=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, verbose_name='职位', null=True)
    behavior_type = models.PositiveSmallIntegerField(choices=BEHAVIOR_TYPE_CHOICES, verbose_name='行为类型')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='行为时间')

    class Meta:
        verbose_name = '用户行为'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['student', 'job']),
        ]

class JobApplication(models.Model):
    """
    Stores the actual application status, separate from the 'Behavior' log used for recommendations.
    When a student applies:
    1. Create JobApplication record.
    2. Create Behavior record (type=3).
    """
    STATUS_CHOICES = (
        (0, '未查看'),
        (1, '已查看'),
        (2, '面试中'),
        (3, '不合适'),
        (4, '通过'),
        (5, '不通过'),
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='applications', verbose_name='学生', null=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications', verbose_name='职位', null=True)
    resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, null=True, verbose_name='投递简历')
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=0, verbose_name='申请状态')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='投递时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return f"{self.student.name} -> {self.job.job_name}"

    class Meta:
        verbose_name = '职位申请'
        verbose_name_plural = verbose_name
        unique_together = ('student', 'job')

class ChatMessage(models.Model):
    sender = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='sent_messages', verbose_name='发送者')
    receiver = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='received_messages', verbose_name='接收者')
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='messages', verbose_name='关联申请')
    content = models.TextField(verbose_name='消息内容')
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='发送时间')

    class Meta:
        verbose_name = '聊天消息'
        verbose_name_plural = verbose_name
        ordering = ['create_time']
