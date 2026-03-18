from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from django.db.models import Q
from .models import Job, JobCategory, MajorCategory
from .serializers import JobSerializer, JobCreateSerializer, JobCategoryTreeSerializer, MajorCategoryTreeSerializer, JobCategoryAdminSerializer, JobCategoryAdminTreeSerializer, MajorCategoryAdminSerializer, MajorCategoryAdminTreeSerializer
from users.models import Company, User
from users.serializers import CompanySerializer
from utils.search import JiebaSearchFilter
import random
import json
import os
import re
import jieba
from django.conf import settings

class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass

class JobFilter(django_filters.FilterSet):
    location = CharInFilter(field_name='location', lookup_expr='in')
    job_category = django_filters.CharFilter(field_name='job_category__name', lookup_expr='icontains')
    major = django_filters.CharFilter(field_name='major__name', lookup_expr='icontains')
    job_name = django_filters.CharFilter(lookup_expr='icontains')
    company_name = django_filters.CharFilter(field_name='company__company_name', lookup_expr='icontains')
    
    class Meta:
        model = Job
        fields = [
            'company', 'location', 'audit_status', 'salary', 'job_type', 
            'degree_requirement', 'experience_requirement',
            'company__industry', 'company__nature', 'company__scale',
            'job_category', 'major'
        ]

class IsCompanyOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 2

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.company.user == request.user

class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 0

class JobPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    # Allow any user to read (list/retrieve) jobs, but only authenticated companies/owners to write
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] 
    filter_backends = [DjangoFilterBackend, JiebaSearchFilter, filters.OrderingFilter]
    filterset_class = JobFilter
    search_fields = ['job_name', 'description', 'requirements', 'company__company_name', 'search_keywords']
    ordering_fields = ['create_time', 'views_count', 'collections_count', 'deliveries_count']
    pagination_class = JobPagination

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve', 'company_categories']:
            return [permissions.AllowAny()]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Allow Admin (role 0) OR Company Owner
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        # Add custom permission check inside method for fine-grained control
        user = request.user
        job = self.get_object()
        
        # Admin can update everything (e.g. audit_status)
        if user.role == 0:
            return super().update(request, *args, **kwargs)
        
        # Company can only update their own jobs
        if user.role == 2:
            if job.company.user != user:
                return Response({"detail": "You do not have permission to edit this job."}, status=status.HTTP_403_FORBIDDEN)
            # Company update logic (reset audit status to pending if content changed?)
            # For now, standard update
            return super().update(request, *args, **kwargs)
            
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        job = self.get_object()
        
        # Admin can delete any job
        if user.role == 0:
            return super().destroy(request, *args, **kwargs)

        # Company can only delete their own jobs
        if user.role == 2:
            if job.company.user != user:
                return Response({"detail": "You do not have permission to delete this job."}, status=status.HTTP_403_FORBIDDEN)
            return super().destroy(request, *args, **kwargs)
            
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

    def get_serializer_class(self):
        if self.action == 'create':
            return JobCreateSerializer
        if self.action in ['update', 'partial_update']:
            # Admin needs to update audit_status, which is not in JobCreateSerializer
            if self.request and self.request.user.is_authenticated and self.request.user.role == 0:
                return JobSerializer
            return JobCreateSerializer
        return JobSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # If 'my_jobs' param is present and user is company, return their jobs
        if self.action == 'list' and self.request.query_params.get('my_jobs') == 'true':
            if user.is_authenticated and user.role == 2:
                try:
                    return queryset.filter(company=user.company_profile)
                except:
                    return queryset.none()
            return queryset.none()

        # For list and retrieve actions:
        if user.is_authenticated:
            # Admin sees all jobs
            if user.role == 0:
                return queryset
            # Companies see approved jobs AND their own jobs (even if not approved).
            elif user.role == 2:
                try:
                    return queryset.filter(Q(audit_status=1) | Q(company=user.company_profile))
                except:
                    return queryset.filter(audit_status=1)
        
        # Public users see only approved jobs.
        return queryset.filter(audit_status=1)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company_profile)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        
        # Log browse behavior if student is logged in
        if request.user.is_authenticated and request.user.role == 1:
            from recruitment.models import Behavior
            Behavior.objects.create(
                student=request.user.student_profile,
                job=instance,
                behavior_type=1 # Browse
            )
            
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='company-categories')
    def company_categories(self, request):
        company_id = request.query_params.get('company')
        if not company_id:
            return Response([])
        
        # Return category names instead of IDs
        categories = Job.objects.filter(
            company_id=company_id, 
            audit_status=1
        ).values_list('job_category__name', flat=True).distinct()
        
        # Filter out empty strings if any
        categories = [c for c in categories if c]
        
        return Response(categories)

    @action(detail=False, methods=['get'], url_path='company-locations')
    def company_locations(self, request):
        company_id = request.query_params.get('company')
        job_category = request.query_params.get('job_category')
        if not company_id:
            return Response([])
        
        queryset = Job.objects.filter(
            company_id=company_id, 
            audit_status=1
        )

        if job_category:
            # Filter by category name
            queryset = queryset.filter(job_category__name=job_category)
            
        locations = queryset.values_list('location', flat=True).distinct()
        
        # Filter out empty strings if any
        locations = [l for l in locations if l]
        
        return Response(locations)

    @action(detail=True, methods=['post'], url_path='apply-takedown')
    def apply_takedown(self, request, pk=None):
        """企业申请下架职位"""
        job = self.get_object()
        user = request.user
        
        # 权限检查：只有发布职位的企业用户可以申请下架
        if user.role != 2 or job.company.user != user:
            return Response({"detail": "您没有权限申请下架此职位"}, status=status.HTTP_403_FORBIDDEN)
            
        reason = request.data.get('reason')
        if not reason:
            return Response({"detail": "请填写下架理由"}, status=status.HTTP_400_BAD_REQUEST)
            
        job.audit_status = 4  # 申请下架
        job.takedown_reason = reason
        job.save()
        
        return Response({"detail": "下架申请已提交，请等待管理员审核"})

    @action(detail=True, methods=['post'], url_path='approve-takedown')
    def approve_takedown(self, request, pk=None):
        """管理员核准或主动下架职位"""
        job = self.get_object()
        user = request.user
        
        # 权限检查：只有管理员可以执行此操作
        if user.role != 0:
            return Response({"detail": "您没有权限执行此操作"}, status=status.HTTP_403_FORBIDDEN)
            
        # 允许对“已通过(1)”或“申请下架(4)”的职位进行下架
        if job.audit_status not in [1, 4]:
            return Response({"detail": "当前职位状态无法执行下架操作"}, status=status.HTTP_400_BAD_REQUEST)
            
        reason = request.data.get('reason')
        if not reason:
            # 如果是企业主动申请的，且管理员没写新理由，可以沿用企业的理由
            if job.audit_status == 4 and job.takedown_reason:
                reason = job.takedown_reason
            else:
                return Response({"detail": "请填写下架理由"}, status=status.HTTP_400_BAD_REQUEST)
            
        job.audit_status = 3  # 已下架
        job.takedown_reason = reason
        job.save()
        
        return Response({"detail": "职位已成功下架"})

    @action(detail=True, methods=['post'], url_path='republish')
    def republish(self, request, pk=None):
        """企业重新上架已下架的职位（进入待审核状态）"""
        job = self.get_object()
        user = request.user
        
        # 权限检查
        if user.role != 2 or job.company.user != user:
            return Response({"detail": "您没有权限上架此职位"}, status=status.HTTP_403_FORBIDDEN)
            
        if job.audit_status != 3:
            return Response({"detail": "只有已下架的职位可以重新上架"}, status=status.HTTP_400_BAD_REQUEST)
            
        job.audit_status = 0  # 待审核
        job.takedown_reason = None # 清空下架理由
        job.save()
        
        return Response({"detail": "职位已重新提交审核"})

class JobCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = JobCategory.objects.all()
    serializer_class = JobCategoryTreeSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return JobCategory.objects.filter(parent__isnull=True).order_by('name')

class MajorCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MajorCategory.objects.all()
    serializer_class = MajorCategoryTreeSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return MajorCategory.objects.filter(parent__isnull=True).order_by('name')

class JobCategoryAdminViewSet(viewsets.ModelViewSet):
    queryset = JobCategory.objects.all()
    serializer_class = JobCategoryAdminSerializer
    permission_classes = [IsAdminRole]
    pagination_class = None

    def list(self, request, *args, **kwargs):
        term = (request.query_params.get('search') or '').strip()
        if not term:
            roots = JobCategory.objects.filter(parent__isnull=True).order_by('name')
            data = JobCategoryAdminTreeSerializer(roots, many=True).data
            return Response(data)

        matches = JobCategory.objects.filter(name__icontains=term).only('id', 'parent_id')
        include_ids = set(matches.values_list('id', flat=True))

        parent_ids = set(matches.values_list('parent_id', flat=True))
        while parent_ids:
            parents = JobCategory.objects.filter(id__in=parent_ids).only('id', 'parent_id')
            new_ids = set(parents.values_list('id', flat=True))
            include_ids |= new_ids
            parent_ids = set(parents.values_list('parent_id', flat=True)) - {None} - include_ids

        nodes = JobCategory.objects.filter(id__in=include_ids).select_related('parent').order_by('name')
        by_id = {n.id: {'id': n.id, 'name': n.name, 'parent': n.parent_id, 'level': n.level, 'path': n.path, 'children': []} for n in nodes}

        roots = []
        for n in nodes:
            item = by_id[n.id]
            if n.parent_id and n.parent_id in by_id:
                by_id[n.parent_id]['children'].append(item)
            else:
                roots.append(item)

        return Response(roots)

class MajorCategoryAdminViewSet(viewsets.ModelViewSet):
    queryset = MajorCategory.objects.all()
    serializer_class = MajorCategoryAdminSerializer
    permission_classes = [IsAdminRole]
    pagination_class = None

    def list(self, request, *args, **kwargs):
        term = (request.query_params.get('search') or '').strip()
        if not term:
            roots = MajorCategory.objects.filter(parent__isnull=True).order_by('name')
            data = MajorCategoryAdminTreeSerializer(roots, many=True).data
            return Response(data)

        matches = MajorCategory.objects.filter(name__icontains=term).only('id', 'parent_id')
        include_ids = set(matches.values_list('id', flat=True))

        parent_ids = set(matches.values_list('parent_id', flat=True))
        while parent_ids:
            parents = MajorCategory.objects.filter(id__in=parent_ids).only('id', 'parent_id')
            new_ids = set(parents.values_list('id', flat=True))
            include_ids |= new_ids
            parent_ids = set(parents.values_list('parent_id', flat=True)) - {None} - include_ids

        nodes = MajorCategory.objects.filter(id__in=include_ids).select_related('parent').order_by('name')
        by_id = {n.id: {'id': n.id, 'name': n.name, 'parent': n.parent_id, 'level': n.level, 'path': n.path, 'children': []} for n in nodes}

        roots = []
        for n in nodes:
            item = by_id[n.id]
            if n.parent_id and n.parent_id in by_id:
                by_id[n.parent_id]['children'].append(item)
            else:
                roots.append(item)

        return Response(roots)

class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        return [permissions.AllowAny()]

    @action(detail=False, methods=['get'], url_path='brand-zone')
    def brand_zone(self, request):
        companies = Company.objects.filter(audit_status=1)
        if companies.count() < 9:
            self._generate_mock_companies()
            companies = Company.objects.filter(audit_status=1)
        
        serializer = CompanySerializer(companies.order_by('?')[:9], many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='selected-jobs')
    def selected_jobs(self, request):
        user = request.user
        limit = 9
        all_approved_jobs = Job.objects.filter(audit_status=1)
        
        # 1. 如果是已登录学生且有求职意向，采用多级推荐策略
        if user.is_authenticated and user.role == 1:
            student = getattr(user, 'student_profile', None)
            if student and student.job_intention:
                from recommendation.models import Recommendation
                final_job_ids = []
                
                # A. 优先尝试 CF 结果 (基于协同过滤)
                recs = Recommendation.objects.filter(
                    student=student, 
                    job__audit_status=1
                ).order_by('-score_hybrid').values_list('job_id', flat=True)[:limit]
                final_job_ids.extend(list(recs))
                
                # B. 如果不足9个，尝试冷启动：关键词匹配求职意向 (Intention Match)
                if len(final_job_ids) < limit:
                    # 使用 jieba 进行中文分词 (搜索引擎模式)
                    # 搜索引擎模式会倾向于将长词切得更细，增加匹配概率
                    jieba_keywords = list(jieba.cut_for_search(student.job_intention))
                    # 过滤掉单字词（通常是助词或意义不大的词）和空白符
                    keywords = [k.strip() for k in jieba_keywords if len(k.strip()) > 1]
                    
                    if not keywords:
                        # 兜底：如果分词后没结果，使用原有的正则简单分词
                        keywords = [k for k in re.split(r'[\s/、,，]+', student.job_intention) if k]
                    
                    if keywords:
                        q_intention = Q()
                        for k in keywords:
                            # 只要 职位名称 或 职位分类 中包含任意一个分词关键词即可
                            q_intention |= Q(job_name__icontains=k) | Q(job_category__name__icontains=k)
                        
                        intention_jobs = all_approved_jobs.filter(q_intention).exclude(id__in=final_job_ids).order_by('?')[:limit - len(final_job_ids)]
                        final_job_ids.extend(list(intention_jobs.values_list('id', flat=True)))
                
                # C. 如果依然不足9个，匹配专业 (Major Match)
                if len(final_job_ids) < limit and student.major:
                    major_jobs = all_approved_jobs.filter(
                        Q(major__name__icontains=student.major) | Q(major_requirement__icontains=student.major)
                    ).exclude(id__in=final_job_ids).order_by('?')[:limit - len(final_job_ids)]
                    final_job_ids.extend(list(major_jobs.values_list('id', flat=True)))
                
                # D. 最后使用热门职位填充 (Popularity Fill)
                if len(final_job_ids) < limit:
                    popular_jobs = all_approved_jobs.exclude(id__in=final_job_ids).order_by('-deliveries_count', '-views_count')[:limit - len(final_job_ids)]
                    final_job_ids.extend(list(popular_jobs.values_list('id', flat=True)))
                
                # 按顺序查询并返回 (保持优先级)
                # 使用 in_bulk 或手动排序
                job_dict = Job.objects.in_bulk(final_job_ids)
                sorted_jobs = [job_dict[jid] for jid in final_job_ids if jid in job_dict]
                serializer = JobSerializer(sorted_jobs, many=True)
                return Response(serializer.data)

        # 2. 兜底逻辑：随机或热门展示
        if all_approved_jobs.count() < limit:
            self._generate_mock_jobs()
            all_approved_jobs = Job.objects.filter(audit_status=1)
            
        # 默认返回热门职位
        final_jobs = all_approved_jobs.order_by('-deliveries_count', '-views_count', '?')[:limit]
        serializer = JobSerializer(final_jobs, many=True)
        return Response(serializer.data)

    def _generate_mock_companies(self):
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

    def _load_json_data(self, filename):
        path = os.path.join(settings.BASE_DIR, '..', 'frontend', 'src', 'assets', filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def _generate_mock_jobs(self):
        # 1. Ensure companies exist
        companies = list(Company.objects.filter(audit_status=1))
        if not companies:
            self._generate_mock_companies()
            companies = list(Company.objects.filter(audit_status=1))
        
        if not companies:
            return

        # 2. Load JSON data
        major_data = self._load_json_data('major.json')
        majors = []
        for l1 in major_data.get('专业分类', []):
            for l2 in l1.get('二级分类列表', []):
                majors.extend(l2.get('三级分类', []))

        job_data = self._load_json_data('jobs.json')
        job_cats = []
        for l1 in job_data.get('职位分类', []):
            for l2 in l1.get('二级分类列表', []):
                job_cats.extend(l2.get('三级分类', []))

        province_data = self._load_json_data('provinces.json')
        locations = []
        for l1 in province_data.get('地区分类', []):
            cities = l1.get('二级分类', [])
            locations.extend([c for c in cities if not c.startswith('全')])
            
        if not majors or not job_cats or not locations:
             # Fallback if files missing
             majors = ['计算机科学与技术', '软件工程', '会计学']
             job_cats = ['Java开发', '产品经理', '销售经理']
             locations = ['北京', '上海', '广州', '深圳']

        # 3. Generate random jobs
        prefixes = ['资深', '高级', '初级', '实习', '助理', '']
        for i in range(20):
            company = random.choice(companies)
            cat_name = random.choice(job_cats)
            major_name = random.choice(majors)
            loc = random.choice(locations)
            title = f"{random.choice(prefixes)}{cat_name}"

            # Try to find existing category instances or create/pick one
            cat_instance = JobCategory.objects.filter(name=cat_name).first()
            major_instance = MajorCategory.objects.filter(name=major_name).first()
            
            # If not found (unlikely if populated properly), skip or handle
            if not cat_instance or not major_instance:
                 continue

            Job.objects.create(
                company=company,
                job_name=title,
                salary=f"{random.randint(4, 25)}k-{random.randint(26, 60)}k" if random.random() > 0.2 else "面议",
                location=loc,
                job_type=random.choice(['全职', '实习']),
                degree_requirement=random.choice(['本科', '硕士', '大专', '学历不限', '博士', '高中', '中专/中技']),
                experience_requirement=random.choice(['无经验', '1-3年', '3-5年', '经验不限', '5-10年']),
                description=f"这是一个关于 {cat_name} 的职位。\n\n岗位职责：\n1. 负责{cat_name}相关工作；\n2. 参与项目需求分析；\n3. 完成上级交代的其他任务。\n\n我们提供有竞争力的薪酬和完善的福利。",
                requirements=f"任职要求：\n1. {major_name}或相关专业优先；\n2. 熟悉相关技能；\n3. 良好的沟通能力和团队协作精神。",
                audit_status=1,
                job_category=cat_instance,
                major=major_instance,
                major_requirement=f"{major_name}及相关专业",
                views_count=random.randint(0, 5000)
            )
