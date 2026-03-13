import os
import sys
import django
import json
import random

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "campus_recruitment_system.settings")
django.setup()

from jobs.models import Job, JobCategory, MajorCategory
from users.models import Company, User
from django.conf import settings
from django.db.models import Q

def load_json(filename):
    # Path to frontend assets: backend/../frontend/src/assets
    path = os.path.join(settings.BASE_DIR, '..', 'frontend', 'src', 'assets', filename)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {path}")
        return {}

def populate_categories():
    print("Populating categories...")
    
    # 1. Majors
    major_data = load_json('major.json')
    MajorCategory.objects.all().delete()
    
    for l1 in major_data.get('专业分类', []):
        cat1 = MajorCategory.objects.create(name=l1['一级分类'], level=1)
        for l2 in l1.get('二级分类列表', []):
            cat2 = MajorCategory.objects.create(name=l2['二级分类'], parent=cat1, level=2)
            for l3_name in l2.get('三级分类', []):
                MajorCategory.objects.create(name=l3_name, parent=cat2, level=3)
                
    # 2. Jobs
    job_data = load_json('jobs.json')
    JobCategory.objects.all().delete()
    
    for l1 in job_data.get('职位分类', []):
        cat1 = JobCategory.objects.create(name=l1['一级分类'], level=1)
        for l2 in l1.get('二级分类列表', []):
            cat2 = JobCategory.objects.create(name=l2['二级分类'], parent=cat1, level=2)
            for l3_name in l2.get('三级分类', []):
                JobCategory.objects.create(name=l3_name, parent=cat2, level=3)
                
    print("Categories populated.")

def get_random_leaf_major():
    # Get level 3 majors
    return MajorCategory.objects.filter(level=3).order_by('?').first()

def get_random_leaf_job_category():
    # Get level 3 job categories
    return JobCategory.objects.filter(level=3).order_by('?').first()

def get_related_major(job_cat_name):
    # Enhanced keyword matching logic
    
    # Direct mappings for common tech roles to CS majors
    tech_keywords = ['前端', '后端', '全栈', '软件', '测试', '运维', 'Java', 'Python', 'C++', 'Go', 'PHP', '算法', '数据', '人工智能', 'AI', '机器', '深度']
    for kw in tech_keywords:
        if kw in job_cat_name:
            # Prioritize Computer Science, Software Engineering, etc.
            cs_majors = MajorCategory.objects.filter(level=3).filter(
                Q(name__icontains='计算机') | 
                Q(name__icontains='软件') | 
                Q(name__icontains='网络') |
                Q(name__icontains='智能')
            )
            if cs_majors.exists():
                return cs_majors.order_by('?').first()

    # General mappings
    keywords = {
        '开发': ['计算机', '软件', '信息', '网络', '通信'],
        '技术': ['计算机', '软件', '信息', '电子'],
        '产品': ['计算机', '软件', '管理', '心理学', '设计', '工业设计'],
        '设计': ['视觉', '美术', '艺术', '设计', '动画', '数字媒体'],
        '运营': ['市场', '新闻', '传播', '中文', '广告', '管理'],
        '市场': ['市场', '营销', '商务', '管理', '经济'],
        '销售': ['市场', '营销', '商务', '管理', '经济'],
        '人事': ['人力资源', '管理', '心理学', '行政', '公共'],
        '行政': ['行政', '管理', '中文', '文秘'],
        '财务': ['会计', '财务', '金融', '经济', '审计'],
        '金融': ['金融', '经济', '投资', '数学', '统计'],
        '银行': ['金融', '经济', '会计'],
        '证券': ['金融', '经济', '投资'],
        '教师': ['教育', '数学', '英语', '物理', '化学', '中文'],
        '教务': ['教育', '管理'],
        '律师': ['法学', '法律'],
        '法务': ['法学', '法律'],
        '医生': ['医学', '临床', '护理'],
        '护士': ['护理'],
        '建筑': ['建筑', '土木', '工程'],
        '土木': ['土木', '工程', '建筑'],
    }
    
    related_keywords = []
    for key, vals in keywords.items():
        if key in job_cat_name:
            related_keywords.extend(vals)
            
    if not related_keywords:
        # Default fallback if no keywords match
        return get_random_leaf_major()
        
    # Search for majors containing these keywords
    query = Q()
    for kw in related_keywords:
        query |= Q(name__icontains=kw)
        
    majors = MajorCategory.objects.filter(level=3).filter(query)
    
    if majors.exists():
        return majors.order_by('?').first()
    else:
        # If we have keywords but found no matching major (rare), try looser match or random
        return get_random_leaf_major()

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

    # 2. Load and Populate Categories
    populate_categories()
    
    # Get all leaf categories for generation
    all_job_cats = JobCategory.objects.filter(level=3)
    locations = get_locations()
    
    if not all_job_cats.exists() or not locations:
        print("Failed to load category data. Aborting.")
        return
        
    print(f"Loaded {all_job_cats.count()} job categories, {len(locations)} locations.")

    # 3. Clear existing jobs
    print("Clearing existing jobs...")
    Job.objects.all().delete()

    # 4. Generate jobs
    print("Generating comprehensive mock jobs...")
    
    # Generate jobs for each job category
    for cat in all_job_cats:
        # Create 1-3 jobs for each category
        for _ in range(random.randint(1, 3)):
            company = random.choice(companies)
            loc = random.choice(locations)
            
            # Find a related major
            major = get_related_major(cat.name)
            
            prefixes = ['资深', '高级', '初级', '实习', '助理', '']
            title = f"{random.choice(prefixes)}{cat.name}"
            
            Job.objects.create(
                company=company,
                job_name=title,
                salary=f"{random.randint(4, 25)}k-{random.randint(26, 60)}k" if random.random() > 0.2 else "面议",
                location=loc,
                job_type=random.choice(['全职', '实习']),
                degree_requirement=random.choice(['本科', '硕士', '大专', '学历不限']),
                experience_requirement=random.choice(['无经验', '1-3年', '3-5年', '经验不限']),
                description=f"这是一个关于 {cat.name} 的职位。\n\n岗位职责：\n1. 负责{cat.name}相关工作；\n2. 参与项目需求分析；\n3. 完成上级交代的其他任务。\n\n我们提供有竞争力的薪酬和完善的福利。",
                requirements=f"任职要求：\n1. {major.name}或相关专业优先；\n2. 熟悉相关技能；\n3. 良好的沟通能力和团队协作精神。",
                audit_status=1,
                
                # New FK fields - passing instances
                job_category=cat,
                major=major,
                
                # Deprecated fields - removed as they are no longer in model definition
                # Or if they are present as dummy fields, we can ignore them or set them if needed.
                # Based on models.py read earlier, job_category IS the FK.
                
                major_requirement=f"{major.name}及相关专业",
                views_count=random.randint(0, 5000)
            )
            
    print("Generating extra random jobs...")
    # Generate extra jobs randomly
    for i in range(200):
        company = random.choice(companies)
        cat = get_random_leaf_job_category()
        major = get_related_major(cat.name)
        loc = random.choice(locations)
        
        prefixes = ['资深', '高级', '初级', '实习', '助理', '']
        title = f"{random.choice(prefixes)}{cat.name}"
        
        Job.objects.create(
            company=company,
            job_name=title,
            salary=f"{random.randint(4, 25)}k-{random.randint(26, 60)}k" if random.random() > 0.2 else "面议",
            location=loc,
            job_type=random.choice(['全职', '实习']),
            degree_requirement=random.choice(['本科', '硕士', '大专', '学历不限']),
            experience_requirement=random.choice(['无经验', '1-3年', '3-5年', '经验不限']),
            description=f"这是一个关于 {cat.name} 的职位。\n\n岗位职责：\n1. 负责{cat.name}相关工作；\n2. 参与项目需求分析；\n3. 完成上级交代的其他任务。\n\n我们提供有竞争力的薪酬和完善的福利。",
            requirements=f"任职要求：\n1. {major.name}或相关专业优先；\n2. 熟悉相关技能；\n3. 良好的沟通能力和团队协作精神。",
            audit_status=1,
            
            # New FK fields - passing instances
            job_category=cat,
            major=major,
            
            major_requirement=f"{major.name}及相关专业",
            views_count=random.randint(0, 5000)
        )

    total_jobs = Job.objects.count()
    print(f"Database population completed successfully! Total jobs: {total_jobs}")

if __name__ == '__main__':
    populate()
