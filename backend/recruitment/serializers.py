from rest_framework import serializers
from .models import Resume, JobApplication, Behavior, ChatMessage
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
    job_detail = JobSerializer(source='job', read_only=True)

    class Meta:
        model = Behavior
        fields = '__all__'
        read_only_fields = ('student', 'create_time')

class ChatMessageSerializer(serializers.ModelSerializer):
    sender_detail = serializers.SerializerMethodField()
    receiver_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = '__all__'
        read_only_fields = ('sender', 'receiver', 'create_time', 'is_read')

    def get_sender_detail(self, obj):
        user = obj.sender
        return self._get_user_info(user)

    def get_receiver_detail(self, obj):
        user = obj.receiver
        return self._get_user_info(user)

    def _get_user_info(self, user):
        if user.role == 1: # Student
            try:
                profile = user.student_profile
                avatar_url = None
                if profile.avatar:
                    request = self.context.get('request')
                    if request:
                        avatar_url = request.build_absolute_uri(profile.avatar.url)
                    else:
                        avatar_url = profile.avatar.url
                
                return {
                    'id': user.id,
                    'name': profile.name or user.username,
                    'avatar': avatar_url,
                    'role': 1
                }
            except:
                return {'id': user.id, 'name': user.username, 'role': 1}
        elif user.role == 2: # Company
            try:
                profile = user.company_profile
                avatar_url = None
                if profile.logo:
                    request = self.context.get('request')
                    if request:
                        avatar_url = request.build_absolute_uri(profile.logo.url)
                    else:
                        avatar_url = profile.logo.url
                
                return {
                    'id': user.id,
                    'name': profile.company_name or user.username,
                    'avatar': avatar_url,
                    'role': 2
                }
            except:
                return {'id': user.id, 'name': user.username, 'role': 2}
        return {'id': user.id, 'name': user.username, 'role': user.role}
