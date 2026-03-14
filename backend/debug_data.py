import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_recruitment_system.settings')
django.setup()

from recruitment.models import JobApplication, Behavior
from django.utils import timezone

print('--- Recent Applications ---')
for app in JobApplication.objects.order_by('-create_time')[:10]:
    print(f'ID: {app.id}, UTC: {app.create_time}, Local: {timezone.localtime(app.create_time)}')

print('\n--- Recent Behaviors ---')
for b in Behavior.objects.order_by('-create_time')[:10]:
    print(f'ID: {b.id}, Type: {b.behavior_type}, UTC: {b.create_time}, Local: {timezone.localtime(b.create_time)}')
