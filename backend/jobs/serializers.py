from rest_framework import serializers
from .models import Job
from users.serializers import CompanySerializer

class JobSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    is_applied = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ('company', 'views_count', 'collections_count', 
                            'deliveries_count', 'create_time', 'update_time', 'is_applied')

    def get_is_applied(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user.role == 1:
            # Avoid circular import
            from recruitment.models import JobApplication
            return JobApplication.objects.filter(student=request.user.student_profile, job=obj).exists()
        return False

class JobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ('job_name', 'salary', 'location', 'description', 'requirements',
                  'job_type', 'degree_requirement', 'experience_requirement',
                  'job_category', 'major', 'major_requirement', 'search_keywords')

    def create(self, validated_data):
        user = self.context['request'].user
        if user.role != 2:
            raise serializers.ValidationError("Only companies can post jobs.")
        
        # Ensure the user has a company profile
        if not hasattr(user, 'company_profile'):
             raise serializers.ValidationError("Company profile not found.")

        validated_data['company'] = user.company_profile
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # If user is company (role 2), reset audit_status to 0 (Pending) on update
        request = self.context.get('request')
        if request and request.user.role == 2:
            instance.audit_status = 0
        return super().update(instance, validated_data)
