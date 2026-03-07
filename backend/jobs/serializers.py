from rest_framework import serializers
from .models import Job
from users.serializers import CompanySerializer

class JobSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    
    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ('company', 'views_count', 'collections_count', 
                            'deliveries_count', 'create_time', 'update_time', 'audit_status')

class JobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ('job_name', 'salary', 'location', 'description', 'requirements')

    def create(self, validated_data):
        user = self.context['request'].user
        if user.role != 2:
            raise serializers.ValidationError("Only companies can post jobs.")
        
        # Ensure the user has a company profile
        if not hasattr(user, 'company_profile'):
             raise serializers.ValidationError("Company profile not found.")

        validated_data['company'] = user.company_profile
        return super().create(validated_data)
