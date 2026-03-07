from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer, StudentSerializer, CompanySerializer
from .models import Student, Company

User = get_user_model()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['username'] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = self.user.role
        data['username'] = self.user.username
        data['id'] = self.user.id
        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
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
