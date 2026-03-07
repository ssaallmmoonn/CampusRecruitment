from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Job
from .serializers import JobSerializer, JobCreateSerializer

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
                return queryset.filter(company=user.company_profile)
            return queryset.none()

        # Default: list only approved jobs
        if self.action == 'list':
            return queryset.filter(audit_status=1)
            
        return queryset

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company_profile)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
