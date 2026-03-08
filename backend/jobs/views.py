from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Job
from .serializers import JobSerializer, JobCreateSerializer
from users.models import Company, User
from users.serializers import CompanySerializer
import random

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

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCompanyOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['location', 'audit_status', 'salary']
    search_fields = ['job_name', 'description', 'requirements', 'company__company_name']
    ordering_fields = ['create_time', 'views_count']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
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
        # Public users see only approved jobs.
        # Companies see approved jobs AND their own jobs (even if not approved).
        if user.is_authenticated and user.role == 2:
            try:
                return queryset.filter(Q(audit_status=1) | Q(company=user.company_profile))
            except:
                return queryset.filter(audit_status=1)
        
        return queryset.filter(audit_status=1)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company_profile)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

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
        jobs = Job.objects.filter(audit_status=1)
        if jobs.count() < 9:
            self._generate_mock_jobs()
            jobs = Job.objects.filter(audit_status=1)
            
        serializer = JobSerializer(jobs.order_by('?')[:9], many=True)
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
                    description=f"{data['name']} is a leading company in {data['industry']} industry."
                )

    def _generate_mock_jobs(self):
        mock_jobs = [
            {'title': '需求分析 (校招, 广州)', 'salary': '9000-13000元', 'company': '广东亿迅-广东亿迅科技有限公司', 'location': '广州', 'type': '全职', 'degree': '本科', 'exp': '无经验', 'industry': '运营商/增值服务', 'scale': '1000-9999人', 'nature': '国企', 'logo': 'https://ui-avatars.com/api/?name=GY&background=0D8ABC&color=fff'},
            {'title': '商品数据分析员', 'salary': '5000-7000元', 'company': '福建三福服饰有限公司', 'location': '广州', 'type': '全职', 'degree': '学历不限', 'exp': '无经验', 'industry': '玩具/礼品', 'scale': '500-999人', 'nature': '民营', 'logo': 'https://ui-avatars.com/api/?name=SF&background=FF5722&color=fff'},
            {'title': '数据分析岗', 'salary': '4000-8000元', 'company': '中国大地保险-大地财险广东', 'location': '广州', 'type': '全职', 'degree': '本科', 'exp': '无经验', 'industry': '保险', 'scale': '10000人以上', 'nature': '国企', 'logo': 'https://ui-avatars.com/api/?name=DD&background=4CAF50&color=fff'},
            {'title': '云售前-广州-26届校招', 'salary': '7000-13000元', 'company': '卓望数码技术 (深圳) 有限公司', 'location': '广州', 'type': '全职', 'degree': '本科', 'exp': '无经验', 'industry': '运营商/增值服务', 'scale': '1000-9999人', 'nature': '外商独资', 'logo': 'https://ui-avatars.com/api/?name=ZW&background=FFC107&color=fff'},
            {'title': '测试工程师', 'salary': '面议', 'company': '思源电气', 'location': '全国', 'type': '全职', 'degree': '本科', 'exp': '经验不限', 'industry': '电气机械/电力设备', 'scale': '1000-9999人', 'nature': '民营', 'logo': 'https://ui-avatars.com/api/?name=SY&background=3F51B5&color=fff'},
            {'title': '系统实施 (校招, 广州)', 'salary': '8000-10000元', 'company': '广东亿迅-广东亿迅科技有限公司', 'location': '广州', 'type': '全职', 'degree': '本科', 'exp': '无经验', 'industry': '运营商/增值服务', 'scale': '1000-9999人', 'nature': '国企', 'logo': 'https://ui-avatars.com/api/?name=GY&background=0D8ABC&color=fff'},
            {'title': '培训生 (设备管理)', 'salary': '面议', 'company': '宝钢股份-上海宝钢国际经济贸易有限公司', 'location': '全国', 'type': '全职', 'degree': '本科', 'exp': '经验不限', 'industry': '钢铁/有色金属冶炼及加工', 'scale': '10000人以上', 'nature': '国企', 'logo': 'https://ui-avatars.com/api/?name=BG&background=607D8B&color=fff'},
            {'title': 'Java助理工程师', 'salary': '面议', 'company': '深圳麦克韦尔科技有限公司-思摩尔', 'location': '全国', 'type': '实习', 'degree': '学历不限', 'exp': '经验不限', 'industry': '电子/半导体/集成...', 'scale': '10000人以上', 'nature': '股份制企业', 'logo': 'https://ui-avatars.com/api/?name=MK&background=009688&color=fff'},
            {'title': '运维岗', 'salary': '面议', 'company': '广东水电二局集团有限公司', 'location': '广州', 'type': '全职', 'degree': '本科', 'exp': '经验不限', 'industry': '工程施工', 'scale': '1000-9999人', 'nature': '国企', 'logo': 'https://ui-avatars.com/api/?name=GS&background=8BC34A&color=fff'},
        ]

        for i, data in enumerate(mock_jobs):
            # Check if company exists, if not create it
            try:
                company = Company.objects.get(company_name=data['company'])
            except Company.DoesNotExist:
                username = f'job_company_mock_{i}'
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(username=username, password='password123', role=2)
                    company = Company.objects.create(
                        user=user,
                        company_name=data['company'],
                        logo=data['logo'],
                        industry=data['industry'],
                        scale=data['scale'],
                        nature=data['nature'],
                        audit_status=1,
                        description=f"{data['company']} description."
                    )
                else:
                    # Fallback if user exists but company doesn't (shouldn't happen with our logic but safe to handle)
                    user = User.objects.get(username=username)
                    if hasattr(user, 'company_profile'):
                        company = user.company_profile
                    else:
                        company = Company.objects.create(
                            user=user,
                            company_name=data['company'],
                            logo=data['logo'],
                            audit_status=1
                        )
            
            # Create Job
            Job.objects.create(
                company=company,
                job_name=data['title'],
                salary=data['salary'],
                location=data['location'],
                job_type=data['type'],
                degree_requirement=data['degree'],
                experience_requirement=data['exp'],
                description=f"Job description for {data['title']}",
                requirements=f"Requirements for {data['title']}",
                audit_status=1
            )
