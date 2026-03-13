from pathlib import Path
import json

from django.db import migrations, models


def _load_job_categories(apps, schema_editor):
    JobCategory = apps.get_model('jobs', 'JobCategory')
    if JobCategory.objects.exists():
        return

    json_path = Path(__file__).resolve().parents[3] / 'frontend' / 'src' / 'assets' / 'jobs.json'
    if not json_path.exists():
        return

    data = json.loads(json_path.read_text(encoding='utf-8'))
    roots = data.get('职位分类', [])

    for l1 in roots:
        l1_name = l1.get('一级分类')
        if not l1_name:
            continue
        l1_obj = JobCategory.objects.create(name=l1_name, parent=None, level=1, path=l1_name[:255])

        for l2 in l1.get('二级分类列表', []):
            l2_name = l2.get('二级分类')
            if not l2_name:
                continue
            l2_path = f'{l1_obj.path}/{l2_name}'[:255]
            l2_obj = JobCategory.objects.create(name=l2_name, parent=l1_obj, level=2, path=l2_path)

            for l3_name in l2.get('三级分类', []) or []:
                if not l3_name:
                    continue
                l3_path = f'{l2_obj.path}/{l3_name}'[:255]
                JobCategory.objects.create(name=l3_name, parent=l2_obj, level=3, path=l3_path)


def _load_major_categories(apps, schema_editor):
    MajorCategory = apps.get_model('jobs', 'MajorCategory')
    if MajorCategory.objects.exists():
        return

    json_path = Path(__file__).resolve().parents[3] / 'frontend' / 'src' / 'assets' / 'major.json'
    if not json_path.exists():
        return

    data = json.loads(json_path.read_text(encoding='utf-8'))
    roots = data.get('专业分类', [])

    for l1 in roots:
        l1_name = l1.get('一级分类')
        if not l1_name:
            continue
        l1_obj = MajorCategory.objects.create(name=l1_name, parent=None, level=1, path=l1_name[:255])

        for l2 in l1.get('二级分类列表', []):
            l2_name = l2.get('二级分类')
            if not l2_name:
                continue
            l2_path = f'{l1_obj.path}/{l2_name}'[:255]
            l2_obj = MajorCategory.objects.create(name=l2_name, parent=l1_obj, level=2, path=l2_path)

            for l3_name in l2.get('三级分类', []) or []:
                if not l3_name:
                    continue
                l3_path = f'{l2_obj.path}/{l3_name}'[:255]
                MajorCategory.objects.create(name=l3_name, parent=l2_obj, level=3, path=l3_path)


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0007_jobcategory_majorcategory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobcategory',
            name='path',
            field=models.CharField(max_length=255, unique=True, verbose_name='路径'),
        ),
        migrations.AlterField(
            model_name='majorcategory',
            name='path',
            field=models.CharField(max_length=255, unique=True, verbose_name='路径'),
        ),
        migrations.RunPython(_load_job_categories, migrations.RunPython.noop),
        migrations.RunPython(_load_major_categories, migrations.RunPython.noop),
    ]

