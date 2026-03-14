import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_recruitment_system.settings')
django.setup()

from recommendation.models import Recommendation
from recruitment.models import JobApplication
from users.models import Student

total_students = Student.objects.count()
recs_count = Recommendation.objects.count()
students_with_recs = Recommendation.objects.values('student').distinct().count()
total_apps = JobApplication.objects.count()
recommended_apps = JobApplication.objects.filter(is_recommended=True).count()

print(f'Total Students: {total_students}')
print(f'Recommendations: {recs_count}')
print(f'Students with Recs: {students_with_recs}')
print(f'Total Apps: {total_apps}')
print(f'Recommended Apps: {recommended_apps}')

# If no recommended apps, check if any application's student+job exists in Recommendation table
if total_apps > 0 and recommended_apps == 0:
    print("\n--- Checking for manual matches (apps that SHOULD be marked recommended) ---")
    for app in JobApplication.objects.all():
        exists = Recommendation.objects.filter(student=app.student, job=app.job).exists()
        if exists:
            print(f"App {app.id} (Student: {app.student_id}, Job: {app.job_id}) IS in Recommendation table but is_recommended=False")
