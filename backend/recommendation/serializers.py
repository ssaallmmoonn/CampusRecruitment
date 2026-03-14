from rest_framework import serializers
from .models import Recommendation
from jobs.serializers import JobSerializer

class RecommendationSerializer(serializers.ModelSerializer):
    job = JobSerializer(read_only=True)
    
    class Meta:
        model = Recommendation
        fields = ('job', 'score_item', 'score_user', 'score_hybrid', 'reason', 'update_time')
