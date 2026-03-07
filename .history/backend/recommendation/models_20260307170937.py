from django.db import models
from users.models import Student
from jobs.models import Job

class Recommendation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='recommendations', verbose_name='推荐学生')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='recommendations', verbose_name='推荐职位')
    score = models.FloatField(default=0.0, verbose_name='推荐得分')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='生成时间')

    def __str__(self):
        return f"{self.student.name} -> {self.job.job_name} ({self.score})"

    class Meta:
        verbose_name = '推荐结果'
        verbose_name_plural = verbose_name
        ordering = ['-score']
        indexes = [
            models.Index(fields=['student', '-score']),
        ]
