from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Resume, JobApplication, Behavior
from .serializers import (
    ResumeSerializer, 
    JobApplicationSerializer, 
    JobApplicationCreateSerializer,
    BehaviorSerializer
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

    def perform_create(self, serializer):
        serializer.save(student=self.request.user.student_profile)

class JobApplicationViewSet(viewsets.ModelViewSet):
    """
    Job Application management.
    - Students can create applications and view their own applications.
    - Companies can view applications for their jobs and update status.
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['create_time', 'update_time']

    def get_serializer_class(self):
        if self.action == 'create':
            return JobApplicationCreateSerializer
        return JobApplicationSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 1: # Student: see own applications
            return JobApplication.objects.filter(student=user.student_profile)
        elif user.role == 2: # Company: see applications for their jobs
            return JobApplication.objects.filter(job__company=user.company_profile)
        return JobApplication.objects.none()

    def perform_create(self, serializer):
        # When creating application, also log 'delivery' behavior (type=3)
        instance = serializer.save(student=self.request.user.student_profile)
        
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

    def get_queryset(self):
        return Behavior.objects.filter(student=self.request.user.student_profile)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user.student_profile)
        
        # If behavior is 'collect' (type=2), update job collection count
        if serializer.validated_data['behavior_type'] == 2:
            job = serializer.validated_data['job']
            job.collections_count += 1
            job.save(update_fields=['collections_count'])
