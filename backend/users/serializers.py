from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Student, Company, Administrator

User = get_user_model()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['username'] = user.username
        return token

    def validate(self, attrs):
        username = attrs.get(self.username_field)
        password = attrs.get('password')

        if username:
            if not User.objects.filter(username=username).exists():
                raise serializers.ValidationError({"detail": "user_not_found"})
            
            user = User.objects.get(username=username)
            if not user.check_password(password):
                raise serializers.ValidationError({"detail": "password_error"})

        data = super().validate(attrs)
        data['role'] = self.user.role
        data['username'] = self.user.username
        data['id'] = self.user.id
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'date_joined')
        read_only_fields = ('id', 'date_joined', 'role')

class AdministratorSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Administrator
        fields = ('user', 'username', 'name', 'avatar', 'phone', 'email')
        read_only_fields = ('user',)

class StudentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Student
        fields = ('user', 'username', 'email', 'name', 'major', 'school', 'education', 'graduation_year', 'phone', 'avatar')
        read_only_fields = ('user',)
    
    def validate_username(self, value):
        request = self.context.get('request')
        if request and request.user:
            user = request.user
            if User.objects.exclude(pk=user.pk).filter(username=value).exists():
                raise serializers.ValidationError("该用户名已存在")
        return value

    def update(self, instance, validated_data):
        # Handle nested user data (username)
        # DRF source='user.username' puts the data in 'user': {'username': '...'}
        user_data = validated_data.pop('user', {})
        username = user_data.get('username')
        
        if username and username != instance.user.username:
            instance.user.username = username
            instance.user.save()
            
        return super().update(instance, validated_data)

class CompanySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Company
        fields = ('id', 'user', 'username', 'email', 'company_name', 'credit_code', 'audit_status', 'reject_reason',
                  'contact_person', 'contact_phone', 'description', 'address',
                  'logo', 'industry', 'scale', 'nature')
        read_only_fields = ('user', 'username', 'email') # Make username and email read-only here

    def update(self, instance, validated_data):
        # If audit_status is being updated, it means admin is approving/rejecting
        # Or if company is updating profile, we should reset audit_status to 0 (Pending)
        
        request = self.context.get('request')
        if request and request.user:
            # If user is company (role 2) and updating their own profile
            if request.user.role == 2:
                # Reset audit status to 0 (Pending)
                validated_data['audit_status'] = 0
                # Clear reject reason
                validated_data['reject_reason'] = ''

        return super().update(instance, validated_data)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)

    # Student specific fields
    name = serializers.CharField(required=False, allow_blank=True)
    major = serializers.CharField(required=False, allow_blank=True)
    school = serializers.CharField(required=False, allow_blank=True)
    education = serializers.CharField(required=False, allow_blank=True)
    graduation_year = serializers.IntegerField(required=False, allow_null=True)
    phone = serializers.CharField(required=False, allow_blank=True)

    # Company specific fields
    company_name = serializers.CharField(required=False, allow_blank=True)
    credit_code = serializers.CharField(required=False, allow_blank=True)
    contact_person = serializers.CharField(required=False, allow_blank=True)
    contact_phone = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'role', 
                  'name', 'major', 'school', 'education', 'graduation_year', 'phone',
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
                school=validated_data.get('school', ''),
                education=validated_data.get('education', ''),
                graduation_year=validated_data.get('graduation_year'),
                email=validated_data.get('email', ''),
                phone=validated_data.get('phone', '')
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

class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "两次输入的密码不一致"})
        if data['new_password'] == data['old_password']:
             raise serializers.ValidationError({"new_password": "新密码不能与旧密码相同"})
        return data
