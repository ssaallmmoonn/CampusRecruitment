from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Student, Company

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'date_joined')
        read_only_fields = ('id', 'date_joined', 'role')

class StudentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Student
        fields = ('user', 'username', 'email', 'name', 'major', 'education', 'graduation_year')
        read_only_fields = ('user',)

class CompanySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Company
        fields = ('user', 'username', 'email', 'company_name', 'credit_code', 'audit_status', 
                  'contact_person', 'contact_phone', 'description', 'address')
        read_only_fields = ('user', 'audit_status')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)

    # Student specific fields
    name = serializers.CharField(required=False)
    major = serializers.CharField(required=False)
    education = serializers.CharField(required=False)
    graduation_year = serializers.IntegerField(required=False)

    # Company specific fields
    company_name = serializers.CharField(required=False)
    credit_code = serializers.CharField(required=False)
    contact_person = serializers.CharField(required=False)
    contact_phone = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'role', 
                  'name', 'major', 'education', 'graduation_year',
                  'company_name', 'credit_code', 'contact_person', 'contact_phone')

    def create(self, validated_data):
        role = validated_data.get('role')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=role
        )

        if role == 1:  # Student
            Student.objects.create(
                user=user,
                name=validated_data.get('name', ''),
                major=validated_data.get('major', ''),
                education=validated_data.get('education', ''),
                graduation_year=validated_data.get('graduation_year')
            )
        elif role == 2:  # Company
            Company.objects.create(
                user=user,
                company_name=validated_data.get('company_name', ''),
                credit_code=validated_data.get('credit_code', ''),
                contact_person=validated_data.get('contact_person', ''),
                contact_phone=validated_data.get('contact_phone', '')
            )
        
        return user
