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

        if not has_changed:
            return Response({'message': '信息无发生更改', 'status': 'unchanged'}, status=status.HTTP_200_OK)

        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
