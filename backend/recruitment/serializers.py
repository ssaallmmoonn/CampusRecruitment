from rest_framework import serializers
from .models import Resume, JobApplication, Behavior
from jobs.serializers import JobSerializer
from users.serializers import StudentSerializer

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = '__all__'
        read_only_fields = ('student', 'create_time', 'update_time')

class JobApplicationSerializer(serializers.ModelSerializer):
    job_detail = JobSerializer(source='job', read_only=True)
    student_detail = StudentSerializer(source='student', read_only=True)
    resume_detail = ResumeSerializer(source='resume', read_only=True)
    
    class Meta:
        model = JobApplication
        fields = ('id', 'student', 'job', 'resume', 'status', 'create_time', 'update_time', 
                  'job_detail', 'student_detail', 'resume_detail')
        read_only_fields = ('student', 'status', 'create_time', 'update_time')

class JobApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ('job', 'resume')

    def validate(self, attrs):
        # Ensure the user is a student
        user = self.context['request'].user
        if user.role != 1:
            raise serializers.ValidationError("Only students can apply for jobs.")
        
        # Ensure student hasn't already applied for this job
        job = attrs.get('job')
        if JobApplication.objects.filter(student=user.student_profile, job=job).exists():
            raise serializers.ValidationError("You have already applied for this job.")
            
        return attrs

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user.student_profile
        return super().create(validated_data)

class BehaviorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Behavior
        fields = '__all__'
        read_only_fields = ('student', 'create_time')
