from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import RegisterSerializer, MyTokenObtainPairSerializer, UserSerializer, StudentSerializer, CompanySerializer, AdministratorSerializer, ChangePasswordSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Student, Company, User, Administrator
from django.shortcuts import get_object_or_404
import random

class IsSystemAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 0

class AdminViewSet(viewsets.ModelViewSet):
    queryset = Administrator.objects.all()
    serializer_class = AdministratorSerializer
    permission_classes = [permissions.IsAuthenticated, IsSystemAdmin]

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

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated, IsSystemAdmin]

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
                # If student profile is missing, it's a data integrity issue.
                # However, returning 404 breaks the frontend login flow if it tries to fetch profile.
                # We should create one or handle it.
                # For now, let's create it if missing (auto-fix) or just raise 404.
                # Raising 404 is correct for "Student Profile", but maybe not for "User Info".
                # But frontend calls /users/profile/ expecting details.
                
                # If we raise 404 here, frontend sees 404.
                from django.http import Http404
                raise Http404("Student profile not found")
        elif user.role == 2:
            try:
                return user.company_profile
            except Company.DoesNotExist:
                from django.http import Http404
                raise Http404("Company profile not found")
        # Role 0 (Admin)
        try:
            return user.admin_profile
        except Administrator.DoesNotExist:
            # Auto-create for existing admin users
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
