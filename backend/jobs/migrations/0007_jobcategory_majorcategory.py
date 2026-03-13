from pathlib import Path
import json

from django.db import migrations, models
import django.db.models.deletion


def _load_job_categories(apps, schema_editor):
    JobCategory = apps.get_model('jobs', 'JobCategory')
    if JobCategory.objects.exists():
        return

    json_path = Path(__file__).resolve().parents[4] / 'frontend' / 'src' / 'assets' / 'jobs.json'
    if not json_path.exists():
        return

    data = json.loads(json_path.read_text(encoding='utf-8'))
    roots = data.get('职位分类', [])

    for l1 in roots:
        l1_name = l1.get('一级分类')
        if not l1_name:
            continue
        l1_obj = JobCategory.objects.create(name=l1_name, parent=None, level=1, path=l1_name)

        for l2 in l1.get('二级分类列表', []):
            l2_name = l2.get('二级分类')
            if not l2_name:
                continue
            l2_path = f'{l1_obj.path}/{l2_name}'
            l2_obj = JobCategory.objects.create(name=l2_name, parent=l1_obj, level=2, path=l2_path)

            for l3_name in l2.get('三级分类', []) or []:
                if not l3_name:
                    continue
                l3_path = f'{l2_obj.path}/{l3_name}'
                JobCategory.objects.create(name=l3_name, parent=l2_obj, level=3, path=l3_path)


def _load_major_categories(apps, schema_editor):
    MajorCategory = apps.get_model('jobs', 'MajorCategory')
    if MajorCategory.objects.exists():
        return

    json_path = Path(__file__).resolve().parents[4] / 'frontend' / 'src' / 'assets' / 'major.json'
    if not json_path.exists():
        return

    data = json.loads(json_path.read_text(encoding='utf-8'))
    roots = data.get('专业分类', [])

    for l1 in roots:
        l1_name = l1.get('一级分类')
        if not l1_name:
            continue
        l1_obj = MajorCategory.objects.create(name=l1_name, parent=None, level=1, path=l1_name)

        for l2 in l1.get('二级分类列表', []):
            l2_name = l2.get('二级分类')
            if not l2_name:
                continue
            l2_path = f'{l1_obj.path}/{l2_name}'
            l2_obj = MajorCategory.objects.create(name=l2_name, parent=l1_obj, level=2, path=l2_path)

            for l3_name in l2.get('三级分类', []) or []:
                if not l3_name:
                    continue
                l3_path = f'{l2_obj.path}/{l3_name}'
                MajorCategory.objects.create(name=l3_name, parent=l2_obj, level=3, path=l3_path)


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0006_alter_job_degree_requirement'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='名称')),
                ('level', models.PositiveSmallIntegerField(verbose_name='层级')),
                ('path', models.CharField(max_length=300, unique=True, verbose_name='路径')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='jobs.jobcategory', verbose_name='父级')),
            ],
            options={
                'verbose_name': '职位分类',
                'verbose_name_plural': '职位分类',
                'unique_together': {('parent', 'name')},
            },
        ),
        migrations.CreateModel(
            name='MajorCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='名称')),
                ('level', models.PositiveSmallIntegerField(verbose_name='层级')),
                ('path', models.CharField(max_length=300, unique=True, verbose_name='路径')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='jobs.majorcategory', verbose_name='父级')),
            ],
            options={
                'verbose_name': '专业分类',
                'verbose_name_plural': '专业分类',
                'unique_together': {('parent', 'name')},
            },
        ),
        migrations.RunPython(_load_job_categories, migrations.RunPython.noop),
        migrations.RunPython(_load_major_categories, migrations.RunPython.noop),
    ]

