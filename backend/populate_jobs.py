import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_recruitment_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import Company
from jobs.models import Job

User = get_user_model()

def create_data():
    print("Creating companies and jobs...")

    companies_data = [
        {"name": "Tech Corp", "user": "tech_hr", "desc": "Leading tech company"},
        {"name": "Finance Inc", "user": "finance_hr", "desc": "Top finance firm"},
        {"name": "Edu Group", "user": "edu_hr", "desc": "Education for everyone"},
        {"name": "Retail Co", "user": "retail_hr", "desc": "Retail giant"},
    ]

    jobs_data = [
        {"title": "Software Engineer", "salary": "20k-30k", "loc": "Beijing", "desc": "Develop web apps"},
        {"title": "Data Analyst", "salary": "15k-25k", "loc": "Shanghai", "desc": "Analyze data"},
        {"title": "Product Manager", "salary": "25k-40k", "loc": "Shenzhen", "desc": "Manage products"},
        {"title": "Frontend Developer", "salary": "18k-28k", "loc": "Hangzhou", "desc": "Vue and React"},
        {"title": "Backend Developer", "salary": "20k-35k", "loc": "Beijing", "desc": "Django and Go"},
        {"title": "HR Specialist", "salary": "10k-15k", "loc": "Chengdu", "desc": "Recruit people"},
        {"title": "Sales Manager", "salary": "12k-20k", "loc": "Wuhan", "desc": "Sell things"},
        {"title": "Marketing Intern", "salary": "3k-5k", "loc": "Shanghai", "desc": "Social media"},
    ]

    for c_data in companies_data:
        username = c_data['user']
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=f"{username}@example.com",
                password="password123",
                role=2
            )
            company = Company.objects.create(
                user=user,
                company_name=c_data['name'],
                credit_code=f"CODE{random.randint(1000,9999)}",
                contact_person="HR Manager",
                contact_phone="13800138000"
            )
            print(f"Created company: {c_data['name']}")
        else:
            company = User.objects.get(username=username).company_profile
            print(f"Company exists: {c_data['name']}")

        # Create 2-4 jobs for each company
        for _ in range(random.randint(2, 4)):
            job_info = random.choice(jobs_data)
            Job.objects.create(
                company=company,
                job_name=job_info['title'],
                salary=job_info['salary'],
                location=job_info['loc'],
                description=f"{job_info['desc']} at {c_data['name']}",
                requirements="Bachelor degree, 1 year experience",
                audit_status=1,  # Approved
                views_count=random.randint(0, 100)
            )
            print(f"  Created job: {job_info['title']}")

if __name__ == '__main__':
    create_data()
