import os
import sys
import django
import json
import random

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "campus_recruitment_system.settings")
django.setup()

from jobs.models import Job
from users.models import Company, User
from django.conf import settings

def load_json(filename):
    # Path to frontend assets: backend/../frontend/src/assets
    path = os.path.join(settings.BASE_DIR, '..', 'frontend', 'src', 'assets', filename)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {path}")
        return {}

def get_majors():
    data = load_json('major.json')
    majors = []
    for l1 in data.get('专业分类', []):
        for l2 in l1.get('二级分类列表', []):
            majors.extend(l2.get('三级分类', []))
    return majors

def get_job_categories():
    data = load_json('jobs.json')
    categories = []
    for l1 in data.get('职位分类', []):
        for l2 in l1.get('二级分类列表', []):
            categories.extend(l2.get('三级分类', []))
    return categories

def get_locations():
    data = load_json('provinces.json')
    locations = []
    for l1 in data.get('地区分类', []):
        cities = l1.get('二级分类', [])
        # Filter out "全xx" if desired, or keep them. 
        # Usually "全xx" represents the whole province. 
        # Let's keep specific cities.
        locations.extend([c for c in cities if not c.startswith('全')])
    return locations

def create_mock_companies():
    mock_data = [
        {'name': '上饶银行股份有限公司', 'image': 'https://images.unsplash.com/photo-1554774853-719586f8c277?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60', 'industry': '金融', 'scale': '1000-9999人', 'nature': '国企'},
        {'name': '迅销(中国)商贸有限公司', 'image': 'https://images.unsplash.com/photo-1556761175-5973dc0f32e7?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60', 'industry': '零售', 'scale': '10000人以上', 'nature': '外商独资'},
        {'name': '货讯通科技(珠海)有限公司', 'image': 'https://images.unsplash.com/photo-1560179707-f14e90ef3623?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60', 'industry': '互联网', 'scale': '500-999人', 'nature': '外商独资'},
        {'name': '上海银行股份有限公司', 'image': 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60', 'industry': '金融', 'scale': '10000人以上', 'nature': '国企'},
        {'name': '中信银行股份有限公司', 'image': 'https://images.unsplash.com/photo-1554469384-e58fac16e23a?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60', 'industry': '金融', 'scale': '10000人以上', 'nature': '股份制企业'},
        {'name': '上海浦东发展银行股份有限公司', 'image': 'https://images.unsplash.com/photo-1497366216548-37526070297c?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60', 'industry': '金融', 'scale': '10000人以上', 'nature': '股份制企业'},
        {'name': '平安银行上海分行', 'image': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60', 'industry': '金融', 'scale': '10000人以上', 'nature': '股份制企业'},
        {'name': '跨境清算公司', 'image': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60', 'industry': '金融', 'scale': '500-999人', 'nature': '国企'},
        {'name': '跃瀚科技2026届春季校园招聘', 'image': 'https://images.unsplash.com/photo-1522071820081-009f0129c71c?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60', 'industry': '互联网', 'scale': '100-499人', 'nature': '民营'},
    ]

    print("Checking/Creating companies...")
    for i, data in enumerate(mock_data):
        username = f'company_mock_{i}'
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username=username, password='password123', role=2)
            Company.objects.create(
                user=user,
                company_name=data['name'],
                logo=data['image'],
                industry=data['industry'],
                scale=data['scale'],
                nature=data['nature'],
                audit_status=1,
                credit_code=f"91440101{random.randint(10000000, 99999999)}",
                description=f"{data['name']} is a leading company in {data['industry']} industry."
            )

def populate():
    # 1. Ensure companies exist
    create_mock_companies()
    
    companies = list(Company.objects.filter(audit_status=1))
    if not companies:
        print("No active companies found. Aborting.")
        return

    # 2. Load JSON data
    majors = get_majors()
    job_cats = get_job_categories()
    locations = get_locations()
    
    if not majors or not job_cats or not locations:
        print("Failed to load JSON data. Aborting.")
        return
        
    print(f"Loaded {len(majors)} majors, {len(job_cats)} job categories, {len(locations)} locations.")

    # 3. Clear existing jobs (Optional: maybe only clear mock jobs? For now, clear all to ensure consistency with new schema)
    # The user asked to "update database", implying getting it in sync.
    print("Clearing existing jobs...")
    Job.objects.all().delete()

    # 4. Generate jobs
    print("Generating 100 mock jobs...")
    prefixes = ['资深', '高级', '初级', '实习', '助理', '']
    
    for i in range(100):
        company = random.choice(companies)
        cat = random.choice(job_cats)
        major = random.choice(majors)
        loc = random.choice(locations)
        
        title = f"{random.choice(prefixes)}{cat}"
        
        Job.objects.create(
            company=company,
            job_name=title,
            salary=f"{random.randint(4, 25)}k-{random.randint(26, 60)}k" if random.random() > 0.2 else "面议",
            location=loc,
            job_type=random.choice(['全职', '实习']),
            degree_requirement=random.choice(['本科', '硕士', '大专', '学历不限', '博士', '高中', '中专/中技']),
            experience_requirement=random.choice(['无经验', '1-3年', '3-5年', '经验不限', '5-10年']),
            description=f"这是一个关于 {cat} 的职位。\n\n岗位职责：\n1. 负责{cat}相关工作；\n2. 参与项目需求分析；\n3. 完成上级交代的其他任务。\n\n我们提供有竞争力的薪酬和完善的福利。",
            requirements=f"任职要求：\n1. {major}或相关专业优先；\n2. 熟悉相关技能；\n3. 良好的沟通能力和团队协作精神。",
            audit_status=1,
            job_category=cat,
            major=major,
            major_requirement=f"{major}及相关专业",
            views_count=random.randint(0, 5000)
        )
    
    print("Database population completed successfully!")

if __name__ == '__main__':
    populate()
