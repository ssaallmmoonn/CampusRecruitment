from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from django.utils import timezone
from django.utils.timezone import make_aware
from django.db.models import Count, Q, Avg, Sum
from recruitment.models import JobApplication, Behavior, Resume
from jobs.models import Job
from recommendation.models import Recommendation
from .serializers import RegisterSerializer, MyTokenObtainPairSerializer, UserSerializer, StudentSerializer, CompanySerializer, AdministratorSerializer, ChangePasswordSerializer, IndustrySerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Student, Company, User, Administrator, Industry
from django.shortcuts import get_object_or_404
import random
import datetime

class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 0

class AdminViewSet(viewsets.ModelViewSet):
    queryset = Administrator.objects.all()
    serializer_class = AdministratorSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        queryset = Administrator.objects.all().order_by('user__date_joined')
        search = self.request.query_params.get('search', None)
        if search:
            from django.db.models import Q
            queryset = queryset.filter(Q(name__icontains=search) | Q(user__username__icontains=search))
        return queryset

    def create(self, request, *args, **kwargs):
        # Custom create logic to handle User creation + Administrator profile
        username = request.data.get('username')
        password = request.data.get('password')
        name = request.data.get('name', '')
        email = request.data.get('email', '')
        phone = request.data.get('phone', '')
        
        if not username or not password:
            return Response({'detail': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({'detail': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email, role=0)
        # Administrator profile is auto-created in get_object usually, but for list view it might not exist yet?
        # Wait, my get_object logic in UserProfileView auto-creates.
        # But here we are creating a new user explicitly.
        # We should create the profile.
        admin_profile = Administrator.objects.create(user=user, name=name, email=email, phone=phone)
        
        serializer = self.get_serializer(admin_profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        user = instance.user
        # Prevent deleting self
        if user.id == self.request.user.id:
             # This should be handled before, but good to have here.
             # DRF doesn't support returning response in perform_destroy easily.
             # We should override destroy.
             pass
        user.delete() 

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user.id == request.user.id:
            return Response({'detail': '不能删除自己.'}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        # Admin can update company info, including audit_status
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Handle audit_status update explicitly if provided
        audit_status = request.data.get('audit_status')
        if audit_status is not None:
            instance.audit_status = audit_status
            
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def batch_delete(self, request):
        ids = request.data.get('ids', []) 
        if not ids:
             return Response({'detail': 'No ids provided.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if request.user.id in ids:
             return Response({'detail': '不能删除自己.'}, status=status.HTTP_400_BAD_REQUEST)

        User.objects.filter(id__in=ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        queryset = Student.objects.all().order_by('user__date_joined')
        search = self.request.query_params.get('search', None)
        if search:
            from django.db.models import Q
            queryset = queryset.filter(Q(name__icontains=search) | Q(user__username__icontains=search))
        return queryset

    def create(self, request, *args, **kwargs):
        # Admin creates student
        username = request.data.get('username')
        password = request.data.get('password')
        name = request.data.get('name', '')
        
        # New fields
        major = request.data.get('major', '')
        school = request.data.get('school', '')
        education = request.data.get('education', '')
        graduation_year = request.data.get('graduation_year')
        phone = request.data.get('phone', '')
        email = request.data.get('email', '')
        
        if not username or not password:
            return Response({'detail': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({'detail': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email, role=1)
        student = Student.objects.create(
            user=user, 
            name=name,
            major=major,
            school=school,
            education=education,
            graduation_year=graduation_year,
            phone=phone,
            email=email
        )
        
        serializer = self.get_serializer(student)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        user = instance.user
        user.delete()

    @action(detail=False, methods=['post'])
    def batch_delete(self, request):
        ids = request.data.get('ids', []) 
        if not ids:
             return Response({'detail': 'No ids provided.'}, status=status.HTTP_400_BAD_REQUEST)
        
        User.objects.filter(id__in=ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class IsCompany(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 2

class AdminDashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 1. Platform Scale
        student_count = Student.objects.count()
        company_count = Company.objects.count()
        job_count = Job.objects.filter(audit_status=1).count()
        application_count = JobApplication.objects.count()

        # 2. Activity & Stickiness (Last 7 days)
        today = timezone.localtime().date()
        last_7_days = [today - timezone.timedelta(days=i) for i in range(6, -1, -1)]
        activity_trends = {date.strftime('%m-%d'): {'views': 0, 'collections': 0, 'applications': 0, 'dau_users': set()} for date in last_7_days}
        
        # Fetch all relevant data for the last 7 days
        start_date = last_7_days[0]
        start_of_period = make_aware(datetime.datetime.combine(start_date, datetime.time.min))
        
        # Aggregate Behaviors (Views & Collections)
        behaviors = Behavior.objects.filter(create_time__gte=start_of_period).values('behavior_type', 'create_time', 'student__user_id')
        for b in behaviors:
            dt = timezone.localtime(b['create_time']).date()
            date_str = dt.strftime('%m-%d')
            if date_str in activity_trends:
                if b['behavior_type'] == 1:
                    activity_trends[date_str]['views'] += 1
                elif b['behavior_type'] == 2:
                    activity_trends[date_str]['collections'] += 1
                activity_trends[date_str]['dau_users'].add(b['student__user_id'])

        # Aggregate Applications
        apps_data = JobApplication.objects.filter(create_time__gte=start_of_period).values('create_time', 'student__user_id')
        for a in apps_data:
            dt = timezone.localtime(a['create_time']).date()
            date_str = dt.strftime('%m-%d')
            if date_str in activity_trends:
                activity_trends[date_str]['applications'] += 1
                activity_trends[date_str]['dau_users'].add(a['student__user_id'])
        
        # Aggregate Logins for DAU
        logins = User.objects.filter(last_login__gte=start_of_period).values('id', 'last_login')
        for l in logins:
            dt = timezone.localtime(l['last_login']).date()
            date_str = dt.strftime('%m-%d')
            if date_str in activity_trends:
                activity_trends[date_str]['dau_users'].add(l['id'])

        # Convert to final list format
        final_trends = []
        for date_str in [d.strftime('%m-%d') for d in last_7_days]:
            data = activity_trends[date_str]
            final_trends.append({
                'date': date_str,
                'views': data['views'],
                'collections': data['collections'],
                'applications': data['applications'],
                'dau': len(data['dau_users'])
            })

        # 3. CF Algorithm Monitoring
        total_students = Student.objects.count()
        students_with_rec = Recommendation.objects.values('student').distinct().count()
        coverage_rate = round(students_with_rec / total_students * 100, 2) if total_students > 0 else 0
        
        recommended_apps = JobApplication.objects.filter(is_recommended=True).count()
        total_apps = JobApplication.objects.count()
        conversion_contribution = round(recommended_apps / total_apps * 100, 2) if total_apps > 0 else 0

        # 4. Recruitment Ecosystem
        # Category distribution
        category_dist = Job.objects.values('job_category__name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        # Supply-Demand Analysis by Category
        category_stats = Job.objects.values('job_category__name').annotate(
            job_count=Count('id', distinct=True),
            total_views=Sum('views_count'),
            total_apps=Sum('deliveries_count')
        )

        tight_jobs = [] # High views, low apps
        competitive_jobs = [] # High apps/job ratio
        
        for cat in category_stats:
            total_views = cat['total_views'] or 0
            total_apps = cat['total_apps'] or 0
            
            if total_views > 0:
                tight_jobs.append({
                    'name': cat['job_category__name'] or '未知',
                    'ratio': round(total_apps / total_views * 100, 2)
                })
            
            if cat['job_count'] > 0:
                competitive_jobs.append({
                    'name': cat['job_category__name'] or '未知',
                    'ratio': round(total_apps / cat['job_count'], 2)
                })
        
        tight_jobs = sorted(tight_jobs, key=lambda x: x['ratio'])[:5]
        competitive_jobs = sorted(competitive_jobs, key=lambda x: x['ratio'], reverse=True)[:5]

        # Heatmap 1: Hour and Weekday (24x7)
        heatmap_24h = []
        for d in range(7):
            for h in range(24):
                heatmap_24h.append([h, d, 0])
        
        # Heatmap 2: Month and Day (12 months x 31 days)
        heatmap_monthly = []
        for m in range(12):
            for d in range(31):
                heatmap_monthly.append([d, m, 0])

        # Python-side aggregation for heatmaps
        all_apps_times = JobApplication.objects.all().values_list('create_time', flat=True)
        for ct in all_apps_times:
            if not ct: continue
            local_ct = timezone.localtime(ct)
            
            h = local_ct.hour
            w = local_ct.weekday() 
            idx_24h = w * 24 + h
            if idx_24h < len(heatmap_24h):
                heatmap_24h[idx_24h][2] += 1
            
            m = local_ct.month - 1
            day = local_ct.day - 1
            idx_monthly = m * 31 + day
            if idx_monthly < len(heatmap_monthly):
                heatmap_monthly[idx_monthly][2] += 1

        return Response({
            'overview': {
                'students': student_count,
                'companies': company_count,
                'jobs': job_count,
                'applications': application_count
            },
            'activity': final_trends,
            'algorithm': {
                'coverage_rate': coverage_rate,
                'conversion_contribution': conversion_contribution
            },
            'ecosystem': {
                'category_distribution': [{'name': item['job_category__name'], 'value': item['count']} for item in category_dist],
                'tight_jobs': tight_jobs,
                'competitive_jobs': competitive_jobs,
                'heatmap_24h': heatmap_24h,
                'heatmap_monthly': heatmap_monthly
            }
        })

class CompanyDashboardView(APIView):
    permission_classes = [IsCompany]

    def get(self, request):
        company = request.user.company_profile
        today = timezone.localtime().date()
        
        import datetime
        from django.utils.timezone import make_aware
        start_of_day = make_aware(datetime.datetime.combine(today, datetime.time.min))
        end_of_day = make_aware(datetime.datetime.combine(today, datetime.time.max))
        
        # 1. Core Metrics
        total_jobs = Job.objects.filter(company=company, audit_status=1).count()
        applications = JobApplication.objects.filter(job__company=company)
        total_applications = applications.count()
        pending_applications = applications.filter(status=0).count()
        
        # Use range for today's stats to avoid timezone issues
        today_applications = applications.filter(create_time__range=(start_of_day, end_of_day)).count()
        today_views = Behavior.objects.filter(
            job__company=company, 
            behavior_type=1, 
            create_time__range=(start_of_day, end_of_day)
        ).count()
        
        # 2. Job Performance (Funnel)
        # Calculate overall averages for the funnel chart
        company_jobs = Job.objects.filter(company=company)
        total_views = company_jobs.aggregate(Sum('views_count'))['views_count__sum'] or 0
        total_collections = company_jobs.aggregate(Sum('collections_count'))['collections_count__sum'] or 0
        total_deliveries = company_jobs.aggregate(Sum('deliveries_count'))['deliveries_count__sum'] or 0
        
        job_count = company_jobs.count() or 1
        avg_views = round(total_views / job_count, 1)
        avg_collections = round(total_collections / job_count, 1)
        avg_deliveries = round(total_deliveries / job_count, 1)

        # Top 10 jobs for the ranking table
        jobs_data = company_jobs.values(
            'id', 'job_name', 'views_count', 'collections_count', 'deliveries_count'
        ).order_by('-deliveries_count')[:10]
        
        funnel_data = []
        for job in jobs_data:
            views = job['views_count'] or 1
            funnel_data.append({
                'name': job['job_name'],
                'views': job['views_count'],
                'collections': job['collections_count'],
                'deliveries': job['deliveries_count'],
                'interest_rate': round(job['collections_count'] / views * 100, 2),
                'apply_rate': round(job['deliveries_count'] / views * 100, 2)
            })
            
        # Overall funnel stats for the chart
        overall_funnel = {
            'avg_views': avg_views,
            'avg_collections': avg_collections,
            'avg_deliveries': avg_deliveries
        }
        
        # Cold jobs warning: views > 10 and apply_rate < 5%
        cold_jobs = []
        for job in company_jobs.filter(views_count__gt=10):
            rate = (job.deliveries_count / job.views_count) * 100
            if rate < 5:
                cold_jobs.append({
                    'name': job.job_name,
                    'views': job.views_count,
                    'deliveries': job.deliveries_count,
                    'rate': round(rate, 2)
                })
        cold_jobs = sorted(cold_jobs, key=lambda x: x['rate'])[:5]

        # 3. CF Algorithm Stats
        recommended_apps = applications.filter(is_recommended=True).count()
        recommendation_rate = round(recommended_apps / total_applications * 100, 2) if total_applications > 0 else 0
        
        # Talent match distribution
        # Fixed query to find recommendations for this company's jobs that were actually applied to
        match_scores = Recommendation.objects.filter(
            job__company=company,
            student__applications__job__company=company 
        ).values('score_hybrid')
        
        high_match = 0
        medium_match = 0
        low_match = 0
        for s in match_scores:
            score = s['score_hybrid'] * 100
            if score >= 80: high_match += 1
            elif score >= 50: medium_match += 1
            else: low_match += 1
            
        match_distribution = [
            {'name': '高匹配 (>80)', 'value': high_match},
            {'name': '中匹配 (50-80)', 'value': medium_match},
            {'name': '低匹配 (<50)', 'value': low_match},
        ]

        # 4. Student Profiling
        applicants_ids = applications.values_list('student', flat=True).distinct()
        students = Student.objects.filter(user_id__in=applicants_ids)
        
        major_dist = students.values('major').annotate(count=Count('major')).order_by('-count')[:8]
        edu_dist = students.values('education').annotate(count=Count('education')).order_by('-count')
        
        # Skill cloud extraction (simplified)
        # Assuming resume content contains skills
        skills_map = {}
        for app in applications.select_related('resume'):
            if app.resume and 'skills' in app.resume.content:
                # Skill can be string or list
                skills = app.resume.content['skills']
                if isinstance(skills, str):
                    skills = [s.strip() for s in skills.split(',')]
                for s in skills:
                    skills_map[s] = skills_map.get(s, 0) + 1
        
        skill_cloud = sorted([{'name': k, 'value': v} for k, v in skills_map.items()], key=lambda x: x['value'], reverse=True)[:20]

        return Response({
            'overview': {
                'total_jobs': total_jobs,
                'total_applications': total_applications,
                'pending_applications': pending_applications,
                'today_applications': today_applications,
                'today_views': today_views,
            },
            'performance': {
                'funnel': funnel_data,
                'overall_funnel': overall_funnel,
                'cold_jobs': cold_jobs
            },
            'algorithm': {
                'recommendation_rate': recommendation_rate,
                'match_distribution': match_distribution
            },
            'profiling': {
                'major_distribution': [{'name': item['major'], 'value': item['count']} for item in major_dist],
                'education_distribution': [{'name': item['education'], 'value': item['count']} for item in edu_dist],
                'skill_cloud': skill_cloud
            }
        })

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        queryset = Company.objects.all().order_by('user__date_joined')
        search = self.request.query_params.get('search', None)
        if search:
            from django.db.models import Q
            queryset = queryset.filter(Q(company_name__icontains=search) | Q(user__username__icontains=search))
        
        audit_status = self.request.query_params.get('audit_status', None)
        if audit_status is not None:
            queryset = queryset.filter(audit_status=audit_status)
            
        return queryset

    def create(self, request, *args, **kwargs):
        # Admin creates company
        username = request.data.get('username')
        password = request.data.get('password')
        company_name = request.data.get('company_name', '')
        
        # New fields
        credit_code = request.data.get('credit_code', '')
        contact_person = request.data.get('contact_person', '')
        contact_phone = request.data.get('contact_phone', '')
        description = request.data.get('description', '')
        address = request.data.get('address', '')
        industry = request.data.get('industry', '')
        scale = request.data.get('scale', '')
        nature = request.data.get('nature', '')
        
        if not username or not password:
            return Response({'detail': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({'detail': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email='', role=2)
        company = Company.objects.create(
            user=user, 
            company_name=company_name,
            credit_code=credit_code,
            contact_person=contact_person,
            contact_phone=contact_phone,
            description=description,
            address=address,
            industry=industry,
            scale=scale,
            nature=nature,
            audit_status=1 # Default approved if created by admin
        )
        
        serializer = self.get_serializer(company)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        user = instance.user
        user.delete()

    @action(detail=False, methods=['post'])
    def batch_delete(self, request):
        ids = request.data.get('ids', []) 
        if not ids:
             return Response({'detail': 'No ids provided.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get users associated with these company profiles
        # ids passed are user_ids (primary key of Company model)
        User.objects.filter(id__in=ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class IndustryViewSet(viewsets.ModelViewSet):
    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'batch_delete']:
            return [permissions.IsAuthenticated(), IsAdminUser()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        queryset = Industry.objects.all().order_by('id')
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

    @action(detail=False, methods=['post'])
    def batch_delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
             return Response({'detail': 'No ids provided.'}, status=status.HTTP_400_BAD_REQUEST)
        Industry.objects.filter(id__in=ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["旧密码错误"]}, status=status.HTTP_400_BAD_REQUEST)
            
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            
            return Response({"message": "密码修改成功，请重新登录"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    authentication_classes = () # Empty tuple to disable authentication for this view
    permission_classes = (permissions.AllowAny,)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    authentication_classes = () # Empty tuple to disable authentication for this view
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        user = self.request.user
        if user.role == 1:
            return StudentSerializer
        elif user.role == 2:
            return CompanySerializer
        # Role 0 (Admin)
        return AdministratorSerializer

    def get_object(self):
        user = self.request.user
        if user.role == 1:
            try:
                return user.student_profile
            except Student.DoesNotExist:
                # Auto-create if missing to prevent 500/404 during profile fetch
                return Student.objects.create(
                    user=user, 
                    name=user.username,
                    education='本科', # Default value
                    major='未填写'
                )
        elif user.role == 2:
            try:
                return user.company_profile
            except Company.DoesNotExist:
                return Company.objects.create(
                    user=user,
                    company_name=user.username,
                    credit_code='未填写'
                )
        # Role 0 or 3 (Admin)
        try:
            return user.admin_profile
        except Administrator.DoesNotExist:
            return Administrator.objects.create(user=user, name=user.username)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Check if data has changed
        has_changed = False
        validated_data = serializer.validated_data
        
        # Check model fields
        for field, value in validated_data.items():
            if hasattr(instance, field):
                current_value = getattr(instance, field)
                if current_value != value:
                    has_changed = True
                    break
        
        # Check if username changed (handled separately because it's on the User model)
        # Note: serializer.validated_data has 'user': {'username': '...'} structure due to source='user.username'
        if 'user' in validated_data and 'username' in validated_data['user']:
             if instance.user.username != validated_data['user']['username']:
                 has_changed = True

        if not has_changed:
            return Response({'message': '信息无发生更改', 'status': 'unchanged'}, status=status.HTTP_200_OK)

        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

class CompanyPublicView(generics.RetrieveUpdateDestroyAPIView):
    """
    Public view for company details
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    lookup_field = 'id'

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        # The frontend passes user_id as company_id because in JobSerializer, 
        # company.id is mapped to company.user.id.
        # So we need to look up the company by its related user's ID.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {'user__id': self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Security check: Ensure the logged-in user owns this company profile OR is admin
        if request.user.id != instance.user.id and request.user.role != 0:
            return Response({'detail': 'You do not have permission to edit this profile.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Check if data has changed
        has_changed = False
        validated_data = serializer.validated_data
        
        # Check model fields
        for field, value in validated_data.items():
            if hasattr(instance, field):
                current_value = getattr(instance, field)
                if current_value != value:
                    has_changed = True
                    break
        
        if not has_changed:
            return Response({'message': '信息无发生更改', 'status': 'unchanged'}, status=status.HTTP_200_OK)

        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Security check: Only admin can delete company profiles via this view
        # (Companies cannot delete themselves currently, unless we want to allow it)
        if request.user.role != 0:
             return Response({'detail': 'You do not have permission to delete this profile.'}, status=status.HTTP_403_FORBIDDEN)
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        user = instance.user
        user.delete()
