import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_recruitment_system.settings')
django.setup()

from recommendation.models import Recommendation
from recruitment.models import JobApplication
from users.models import Student
from jobs.models import Job

try:
    student = Student.objects.get(pk=11)
    # Pick a job not already applied by the student
    applied_job_ids = JobApplication.objects.filter(student=student).values_list('job_id', flat=True)
    job = Job.objects.filter(audit_status=1).exclude(id__in=applied_job_ids).first()
    
    if job:
        Recommendation.objects.create(
            student=student,
            job=job,
            score_item=0.9,
            score_user=0.1,
            score_hybrid=0.5,
            reason=[{'type': 'mock', 'text': '为了演示效果生成的模拟推荐'}]
        )
        print(f"Created recommendation for Student {student.pk} and Job {job.pk}")
    
    # Mark one application as recommended to test conversion
    app = JobApplication.objects.filter(student=student).first()
    if app:
        app.is_recommended = True
        app.save()
        print(f"Marked App {app.id} as recommended.")

except Exception as e:
    print(f"Error: {e}")
