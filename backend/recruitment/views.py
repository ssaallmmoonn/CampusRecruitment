from django.db import models
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Resume, JobApplication, Behavior, ChatMessage
from .serializers import (
    ResumeSerializer, 
    JobApplicationSerializer, 
    JobApplicationCreateSerializer,
    BehaviorSerializer,
    ChatMessageSerializer
)
from jobs.models import Job

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 1

class IsCompany(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 2

class ResumeViewSet(viewsets.ModelViewSet):
    """
    Resume management for students.
    Students can CRUD their own resumes.
    Companies can view resumes through job applications (handled there).
    """
    serializer_class = ResumeSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        return Resume.objects.filter(student=self.request.user.student_profile)




    def create(self, request, *args, **kwargs):
        # Check if already applied
        job_id = request.data.get('job')
        if job_id:
             try:
                 student = request.user.student_profile
                 if JobApplication.objects.filter(student=student, job_id=job_id).exists():
                     return Response(
                         {'detail': '您已经投递过该职位，请勿重复投递'}, 
                         status=status.HTTP_400_BAD_REQUEST
                     )
             except Exception:
                 # In case user has no student profile or other error
                 pass
        
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user.student_profile)

class JobApplicationViewSet(viewsets.ModelViewSet):
    """
    Job Application management.
    - Students can create applications and view their own applications.
    - Companies can view applications for their jobs and update status.
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['status']
    search_fields = ['job__job_name', 'student__name', 'student__user__username']
    ordering_fields = ['create_time', 'update_time', 'unread_count']

    def get_serializer_class(self):
        if self.action == 'create':
            return JobApplicationCreateSerializer
        return JobApplicationSerializer

    def get_queryset(self):
        user = self.request.user
        from django.db.models import Count, Q
        
        if user.role == 1: # Student: see own applications
            queryset = JobApplication.objects.filter(student=user.student_profile)
            # Annotate with unread messages count (where receiver is student)
            queryset = queryset.annotate(
                unread_count=Count('messages', filter=Q(messages__receiver=user, messages__is_read=False))
            )
        elif user.role == 2: # Company: see applications for their jobs
            queryset = JobApplication.objects.filter(job__company=user.company_profile).select_related('student', 'job', 'resume')
            # Annotate with unread messages count (where receiver is company user)
            queryset = queryset.annotate(
                unread_count=Count('messages', filter=Q(messages__receiver=user, messages__is_read=False))
            )
        else:
            queryset = JobApplication.objects.none()
            
        return queryset

    def filter_queryset(self, queryset):
        # Apply standard filters first
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
            
        ordering = self.request.query_params.get('ordering')
        if ordering == '-unread_count':
            # Custom sorting logic:
            # Sort by unread_count DESC, then create_time DESC (New -> Old)
            # This satisfies: "If any unread, they come first (sorted by unread count). If none, sorted by time."
            # Actually if unread_count is 0 for all, it falls back to create_time DESC.
            queryset = queryset.order_by('-unread_count', '-create_time')
            
        return queryset

    def perform_create(self, serializer):
        # When creating application, also log 'delivery' behavior (type=3)
        instance = serializer.save()
        
        # Log behavior
        Behavior.objects.create(
            student=instance.student,
            job=instance.job,
            behavior_type=3 # Delivery
        )
        
        # Update job delivery count
        job = instance.job
        job.deliveries_count += 1
        job.save(update_fields=['deliveries_count'])

    @action(detail=False, methods=['get'])
    def check_status(self, request):
        """
        Check if a job is applied.
        """
        job_id = request.query_params.get('job_id')
        if not job_id:
            return Response({'error': 'job_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        student = request.user.student_profile
        application = JobApplication.objects.filter(student=student, job_id=job_id).first()
        
        if application:
            return Response({'applied': True, 'application_id': application.id})
        return Response({'applied': False})
    @action(detail=True, methods=['post'], permission_classes=[IsCompany])
    def update_status(self, request, pk=None):
        """
        Company updates application status (e.g. mark as viewed, interested, rejected)
        """
        application = self.get_object()
        new_status = request.data.get('status')
        
        if new_status is None:
            return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            new_status = int(new_status)
            if new_status not in [choice[0] for choice in JobApplication.STATUS_CHOICES]:
                raise ValueError
        except ValueError:
            return Response({'error': 'Invalid status value'}, status=status.HTTP_400_BAD_REQUEST)

        application.status = new_status
        application.save()
        return Response({'status': 'updated'})

class BehaviorViewSet(viewsets.ModelViewSet):
    """
    Log user behaviors (Browse, Collect).
    Delivery behavior is logged automatically when applying.
    """
    serializer_class = BehaviorSerializer
    permission_classes = [IsStudent]
    http_method_names = ['post', 'get', 'delete'] # Only allow creating/viewing logs
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['behavior_type']
    ordering_fields = ['create_time']

    def get_queryset(self):
        return Behavior.objects.filter(student=self.request.user.student_profile)

    def filter_queryset(self, queryset):
        # Apply standard filters first
        # But we must be careful not to call super().filter_queryset() if it doesn't exist on ModelViewSet
        # Actually ModelViewSet uses filter_backends.
        
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)

        # Custom filtering for job properties (which are in job_detail/job relation)
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(job__job_name__icontains=search)

        is_applied = self.request.query_params.get('is_applied')
        if is_applied is not None:
            user = self.request.user
            # We need to filter based on whether THIS user has applied for the job
            # The job is related via 'job' field on Behavior
            # JobApplication has 'student' and 'job'
            # We want Behaviors where behavior.job has a JobApplication by this student
            
            applied_jobs = JobApplication.objects.filter(student__user=user).values_list('job_id', flat=True)
            
            if is_applied.lower() == 'true':
                queryset = queryset.filter(job__id__in=applied_jobs)
            elif is_applied.lower() == 'false':
                queryset = queryset.exclude(job__id__in=applied_jobs)
        
        location = self.request.query_params.get('location')
        if location:
            queryset = queryset.filter(job__location__icontains=location)
            
        # Custom ordering
        ordering = self.request.query_params.get('ordering')
        if ordering:
             if ordering == 'salary' or ordering == '-salary':
                 # Extract number before 'k' from salary string (e.g. '12k-20k' -> 12)
                 from django.db.models import Case, When, Value, IntegerField
                 from django.db.models.functions import Substr, StrIndex, Cast, Lower
                 
                 # Logic: 
                 # 1. Lowercase the salary string
                 # 2. Find index of 'k'
                 # 3. Substr from start to 'k'-1
                 # 4. Cast to integer
                 # This assumes salary format is always like "XXk..." or "Xk..."
                 
                 queryset = queryset.annotate(
                     salary_num=Cast(
                         Substr(
                             Lower('job__salary'), 
                             1, 
                             StrIndex(Lower('job__salary'), Value('k')) - 1
                         ),
                         IntegerField()
                     )
                 )
                 
                 if ordering == 'salary':
                     queryset = queryset.order_by('salary_num')
                 else:
                     queryset = queryset.order_by('-salary_num')
                     
             elif ordering == 'deliveries': # 投递时间 (Old -> New)
                  from django.db.models import Max
                  from django.db.models import F
                  
                  # 1. Annotate app_time
                  queryset = queryset.annotate(
                      app_time=Max('job__applications__create_time', 
                                   filter=models.Q(job__applications__student__user=self.request.user))
                  )
                  
                  # 2. Filter out unapplied jobs (app_time is NULL)
                  queryset = queryset.filter(app_time__isnull=False)
                  
                  # 3. Sort: applied jobs (by time ASC)
                  queryset = queryset.order_by('app_time') 
                  
             elif ordering == '-deliveries': # 投递时间 (New -> Old)
                  from django.db.models import Max, F
                  
                  # 1. Annotate app_time
                  queryset = queryset.annotate(
                      app_time=Max('job__applications__create_time', 
                                   filter=models.Q(job__applications__student__user=self.request.user))
                  )
                  
                  # 2. Filter out unapplied jobs (app_time is NULL)
                  queryset = queryset.filter(app_time__isnull=False)
                  
                  # 3. Sort: applied jobs (by time DESC)
                  queryset = queryset.order_by('-app_time')

             elif ordering == 'create_time': # 收藏时间 (Old -> New)
                 queryset = queryset.order_by('create_time')

             elif ordering == '-create_time': # 收藏时间 (New -> Old)
                 queryset = queryset.order_by('-create_time')

        return queryset

    def perform_create(self, serializer):
        # Check if behavior already exists (e.g. repeated collections)
        student = self.request.user.student_profile
        job = serializer.validated_data['job']
        behavior_type = serializer.validated_data['behavior_type']
        
        if behavior_type == 2: # Collection
             # Prevent duplicate collections
             if Behavior.objects.filter(student=student, job=job, behavior_type=2).exists():
                 # Already collected, do nothing or raise error. 
                 # For idempotent behavior, we can just return.
                 return 
        
        serializer.save(student=student)
        
        # If behavior is 'collect' (type=2), update job collection count
        if behavior_type == 2:
            job.collections_count += 1
            job.save(update_fields=['collections_count'])

    @action(detail=False, methods=['post'])
    def toggle_collect(self, request):
        """
        Toggle collection status for a job.
        If collected, remove collection. If not, add collection.
        """
        job_id = request.data.get('job_id')
        if not job_id:
            return Response({'error': 'job_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
            
        student = request.user.student_profile
        behavior = Behavior.objects.filter(student=student, job=job, behavior_type=2).first()
        
        if behavior:
            # Already collected, remove it
            behavior.delete()
            if job.collections_count > 0:
                job.collections_count -= 1
                job.save(update_fields=['collections_count'])
            return Response({'collected': False, 'msg': '已取消收藏'})
        else:
            # Not collected, add it
            Behavior.objects.create(student=student, job=job, behavior_type=2)
            job.collections_count += 1
            job.save(update_fields=['collections_count'])
            return Response({'collected': True, 'msg': '收藏成功'})

    @action(detail=False, methods=['get'])
    def check_status(self, request):
        """
        Check if a job is collected.
        """
        job_id = request.query_params.get('job_id')
        if not job_id:
            return Response({'error': 'job_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        student = request.user.student_profile
        is_collected = Behavior.objects.filter(student=student, job_id=job_id, behavior_type=2).exists()
        
        return Response({'collected': is_collected})

class ChatMessageViewSet(viewsets.ModelViewSet):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['application']
    ordering_fields = ['create_time']

    def get_queryset(self):
        user = self.request.user
        if user.role == 1: # Student
            # Return messages for applications where student is self
            return ChatMessage.objects.filter(application__student__user=user)
        elif user.role == 2: # Company
            # Return messages for applications where job company is self
            return ChatMessage.objects.filter(application__job__company__user=user)
        return ChatMessage.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        application = serializer.validated_data['application']
        
        # Determine receiver
        if user.role == 1: # Student sending
            if application.student.user != user:
                from rest_framework import exceptions
                raise exceptions.PermissionDenied("You can only send messages for your own applications.")
            receiver = application.job.company.user
        elif user.role == 2: # Company sending
            if application.job.company.user != user:
                 from rest_framework import exceptions
                 raise exceptions.PermissionDenied("You can only send messages for your company's jobs.")
            receiver = application.student.user
        else:
             from rest_framework import exceptions
             raise exceptions.PermissionDenied("Invalid user role.")

        serializer.save(sender=user, receiver=receiver)

    @action(detail=False, methods=['post'])
    def mark_read(self, request):
        """
        Mark all messages in an application as read for the current user.
        """
        application_id = request.data.get('application_id')
        if not application_id:
            return Response({'error': 'application_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        # Mark messages where receiver is current user and application is given ID
        ChatMessage.objects.filter(application=application_id, receiver=user, is_read=False).update(is_read=True)
        
        return Response({'status': 'ok'})
