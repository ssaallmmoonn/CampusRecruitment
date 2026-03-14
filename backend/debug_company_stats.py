import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_recruitment_system.settings')
django.setup()

from jobs.models import Job
from users.models import Company, User
from recruitment.models import JobApplication, Behavior

# Debug for a specific company (Assuming we can find the one the user is using)
# Or just list all companies and their stats
print("--- Company Stats Debug ---")
companies = Company.objects.all()
for c in companies:
    jobs = Job.objects.filter(company=c)
    total_views = sum(j.views_count for j in jobs)
    total_colls = sum(j.collections_count for j in jobs)
    total_apps = sum(j.deliveries_count for j in jobs)
    
    actual_apps = JobApplication.objects.filter(job__company=c).count()
    actual_behaviors = Behavior.objects.filter(job__company=c).count()
    
    print(f"Company: {c.company_name} (User: {c.user.username})")
    print(f"  Jobs: {jobs.count()}")
    print(f"  Counter Views: {total_views}, Collections: {total_colls}, Deliveries: {total_apps}")
    print(f"  Actual Apps: {actual_apps}, Actual Behaviors: {actual_behaviors}")
    
    if jobs.count() > 0:
        top_job = jobs.order_by('-deliveries_count').first()
        print(f"  Top Job: {top_job.job_name} (V:{top_job.views_count}, C:{top_job.collections_count}, D:{top_job.deliveries_count})")
