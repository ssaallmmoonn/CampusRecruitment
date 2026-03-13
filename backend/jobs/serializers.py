from rest_framework import serializers
from .models import Job, JobCategory, MajorCategory
from users.serializers import CompanySerializer

class JobCategoryTreeSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source='name', read_only=True)
    value = serializers.CharField(source='path', read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = JobCategory
        fields = ('label', 'value', 'children')

    def get_children(self, obj):
        qs = obj.children.all().order_by('name')
        return JobCategoryTreeSerializer(qs, many=True).data

class MajorCategoryTreeSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source='name', read_only=True)
    value = serializers.CharField(source='path', read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = MajorCategory
        fields = ('label', 'value', 'children')

    def get_children(self, obj):
        qs = obj.children.all().order_by('name')
        return MajorCategoryTreeSerializer(qs, many=True).data

class JobCategoryAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = ('id', 'name', 'parent', 'level', 'path')
        read_only_fields = ('level', 'path')

    def validate(self, attrs):
        parent = attrs.get('parent')
        if self.instance is not None and 'parent' not in attrs:
            parent = self.instance.parent
        level = 1
        if parent is not None:
            level = (parent.level or 1) + 1
        if level > 3:
            raise serializers.ValidationError({'parent': '仅支持三级分类'})
        return attrs

    def create(self, validated_data):
        parent = validated_data.get('parent')
        if parent is None:
            level = 1
            path = validated_data['name']
        else:
            level = (parent.level or 1) + 1
            path = f'{parent.path}/{validated_data["name"]}'

        instance = JobCategory.objects.create(
            name=validated_data['name'],
            parent=parent,
            level=level,
            path=path[:255],
        )
        return instance

    def update(self, instance, validated_data):
        old_path = instance.path
        instance.name = validated_data.get('name', instance.name)
        if 'parent' in validated_data:
            instance.parent = validated_data['parent']

        parent = instance.parent
        if parent is None:
            instance.level = 1
            instance.path = instance.name
        else:
            instance.level = (parent.level or 1) + 1
            if instance.level > 3:
                raise serializers.ValidationError({'parent': '仅支持三级分类'})
            instance.path = f'{parent.path}/{instance.name}'

        instance.path = instance.path[:255]
        instance.save()

        new_path = instance.path
        if old_path != new_path:
            descendants = JobCategory.objects.filter(path__startswith=old_path + '/')
            for node in descendants:
                node.path = (new_path + node.path[len(old_path):])[:255]
                node.save(update_fields=['path'])

        return instance

class JobCategoryAdminTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = JobCategory
        fields = ('id', 'name', 'parent', 'level', 'path', 'children')

    def get_children(self, obj):
        qs = obj.children.all().order_by('name')
        return JobCategoryAdminTreeSerializer(qs, many=True).data

class MajorCategoryAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = MajorCategory
        fields = ('id', 'name', 'parent', 'level', 'path')
        read_only_fields = ('level', 'path')

    def validate(self, attrs):
        parent = attrs.get('parent')
        if self.instance is not None and 'parent' not in attrs:
            parent = self.instance.parent
        level = 1
        if parent is not None:
            level = (parent.level or 1) + 1
        if level > 3:
            raise serializers.ValidationError({'parent': '仅支持三级分类'})
        return attrs

    def create(self, validated_data):
        parent = validated_data.get('parent')
        if parent is None:
            level = 1
            path = validated_data['name']
        else:
            level = (parent.level or 1) + 1
            path = f'{parent.path}/{validated_data["name"]}'

        instance = MajorCategory.objects.create(
            name=validated_data['name'],
            parent=parent,
            level=level,
            path=path[:255],
        )
        return instance

    def update(self, instance, validated_data):
        old_path = instance.path
        instance.name = validated_data.get('name', instance.name)
        if 'parent' in validated_data:
            instance.parent = validated_data['parent']

        parent = instance.parent
        if parent is None:
            instance.level = 1
            instance.path = instance.name
        else:
            instance.level = (parent.level or 1) + 1
            if instance.level > 3:
                raise serializers.ValidationError({'parent': '仅支持三级分类'})
            instance.path = f'{parent.path}/{instance.name}'

        instance.path = instance.path[:255]
        instance.save()

        new_path = instance.path
        if old_path != new_path:
            descendants = MajorCategory.objects.filter(path__startswith=old_path + '/')
            for node in descendants:
                node.path = (new_path + node.path[len(old_path):])[:255]
                node.save(update_fields=['path'])

        return instance

class MajorCategoryAdminTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = MajorCategory
        fields = ('id', 'name', 'parent', 'level', 'path', 'children')

    def get_children(self, obj):
        qs = obj.children.all().order_by('name')
        return MajorCategoryAdminTreeSerializer(qs, many=True).data

class JobSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    is_applied = serializers.SerializerMethodField()
    # Use StringRelatedField to return the name of the category instead of ID
    job_category = serializers.StringRelatedField()
    major = serializers.StringRelatedField()
    
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

    def validate_job_category(self, value):
        if not value:
            raise serializers.ValidationError('请选择职位分类')
        if '/' in value:
            ok = JobCategory.objects.filter(level=3, path=value).exists()
        else:
            ok = JobCategory.objects.filter(level=3, name=value).exists()
        if not ok:
            raise serializers.ValidationError('职位分类不合法')
        return value

    def validate_major(self, value):
        if not value:
            raise serializers.ValidationError('请选择专业分类')
        if '/' in value:
            ok = MajorCategory.objects.filter(level=3, path=value).exists()
        else:
            ok = MajorCategory.objects.filter(level=3, name=value).exists()
        if not ok:
            raise serializers.ValidationError('专业分类不合法')
        return value

class JobCreateSerializer(serializers.ModelSerializer):
    # Explicitly declare as CharField to accept strings from frontend
    job_category = serializers.CharField(required=True)
    major = serializers.CharField(required=True)
    
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
        
        # Convert string names to model instances for ForeignKeys
        # Note: validate_job_category and validate_major ensure these exist
        if 'job_category' in validated_data and isinstance(validated_data['job_category'], str):
             name = validated_data['job_category']
             # Assuming name is unique at level 3 or path is provided. 
             # The validator checks for level=3.
             # We try to find by path first, then name.
             if '/' in name:
                 validated_data['job_category'] = JobCategory.objects.get(path=name, level=3)
             else:
                 # This might be ambiguous if multiple categories have same name, 
                 # but for now pick the first one matching level 3.
                 validated_data['job_category'] = JobCategory.objects.filter(name=name, level=3).first()

        if 'major' in validated_data and isinstance(validated_data['major'], str):
             name = validated_data['major']
             if '/' in name:
                 validated_data['major'] = MajorCategory.objects.get(path=name, level=3)
             else:
                 validated_data['major'] = MajorCategory.objects.filter(name=name, level=3).first()
                 
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # If user is company (role 2), reset audit_status to 0 (Pending) on update
        request = self.context.get('request')
        if request and request.user.role == 2:
            instance.audit_status = 0
            
        # Convert string names to model instances for ForeignKeys
        if 'job_category' in validated_data and isinstance(validated_data['job_category'], str):
             name = validated_data['job_category']
             if '/' in name:
                 validated_data['job_category'] = JobCategory.objects.get(path=name, level=3)
             else:
                 validated_data['job_category'] = JobCategory.objects.filter(name=name, level=3).first()

        if 'major' in validated_data and isinstance(validated_data['major'], str):
             name = validated_data['major']
             if '/' in name:
                 validated_data['major'] = MajorCategory.objects.get(path=name, level=3)
             else:
                 validated_data['major'] = MajorCategory.objects.filter(name=name, level=3).first()
                 
        return super().update(instance, validated_data)

    def validate_job_category(self, value):
        if not value:
            raise serializers.ValidationError('请选择职位分类')
        if '/' in value:
            ok = JobCategory.objects.filter(level=3, path=value).exists()
        else:
            ok = JobCategory.objects.filter(level=3, name=value).exists()
        if not ok:
            raise serializers.ValidationError('职位分类不合法')
        return value

    def validate_major(self, value):
        if not value:
            raise serializers.ValidationError('请选择专业分类')
        if '/' in value:
            ok = MajorCategory.objects.filter(level=3, path=value).exists()
        else:
            ok = MajorCategory.objects.filter(level=3, name=value).exists()
        if not ok:
            raise serializers.ValidationError('专业分类不合法')
        return value
