from rest_framework import serializers
from .models import Banner, Brand
from users.serializers import CompanySerializer

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'

class BrandSerializer(serializers.ModelSerializer):
    company_detail = CompanySerializer(source='company', read_only=True)

    class Meta:
        model = Brand
        fields = '__all__'
