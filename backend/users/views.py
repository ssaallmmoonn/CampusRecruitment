from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import RegisterSerializer, MyTokenObtainPairSerializer, UserSerializer, StudentSerializer, CompanySerializer, ChangePasswordSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Student, Company, User
from django.shortcuts import get_object_or_404
import random

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
        return UserSerializer

    def get_object(self):
        user = self.request.user
        if user.role == 1:
            try:
                return user.student_profile
            except Student.DoesNotExist:
                # Should not happen if registered correctly, but handle it
                from django.http import Http404
                raise Http404("Student profile not found")
        elif user.role == 2:
            try:
                return user.company_profile
            except Company.DoesNotExist:
                from django.http import Http404
                raise Http404("Company profile not found")
        return user

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

class CompanyPublicView(generics.RetrieveUpdateAPIView):
    """
    Public view for company details
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    # Allow Any for GET, but IsAuthenticated for PUT/PATCH (and maybe check if it's the owner)
    # But generics.RetrieveUpdateAPIView uses one permission class list.
    # We can override get_permissions.
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
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
        
        # Security check: Ensure the logged-in user owns this company profile
        if request.user.id != instance.user.id:
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
