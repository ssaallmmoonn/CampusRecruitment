from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from .models import Recommendation
from .serializers import RecommendationSerializer
from jobs.models import Job
from jobs.serializers import JobSerializer
from django.db.models import Q, Count

class RecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Recommendation viewset for students.
    """
    serializer_class = RecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only students get recommendations
        if self.request.user.role != 1:
            return Recommendation.objects.none()
        
        student = self.request.user.student_profile
        strategy = self.request.query_params.get('strategy', 'hybrid')
        
        # Filtering parameters
        location = self.request.query_params.get('location')
        degree = self.request.query_params.get('degree_requirement')
        job_type = self.request.query_params.get('job_type')
        nature = self.request.query_params.get('company_nature')
        
        queryset = Recommendation.objects.filter(student=student)
        
        if location:
            queryset = queryset.filter(job__location__icontains=location)
        if degree:
            queryset = queryset.filter(job__degree_requirement=degree)
        if job_type:
            queryset = queryset.filter(job__job_type=job_type)
        if nature:
            queryset = queryset.filter(job__company__nature=nature)
        
        if strategy == 'item':
            # Jobs similar to user's history
            return queryset.filter(score_item__gt=0).order_by('-score_item')
        elif strategy == 'user':
            # Jobs from similar users
            return queryset.filter(score_user__gt=0).order_by('-score_user')
        else:
            # Default hybrid
            return queryset.order_by('-score_hybrid')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # If no CF recommendations found, use cold start strategy
        if not queryset.exists() and request.user.role == 1:
            return self._cold_start_recommendations(request)
        
        # Implement pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def _cold_start_recommendations(self, request):
        """
        Cold start strategy:
        1. Match by job_intention / job_category
        2. Match by major
        3. Popular jobs
        """
        student = request.user.student_profile
        job_intention = student.job_intention
        major = student.major
        
        # Pagination params
        try:
            limit = int(request.query_params.get('limit', 20))
            offset = int(request.query_params.get('offset', 0))
        except ValueError:
            limit = 20
            offset = 0

        # Filtering parameters for cold start
        location = request.query_params.get('location')
        degree = request.query_params.get('degree_requirement')
        job_type = request.query_params.get('job_type')
        nature = request.query_params.get('company_nature')
        
        # 1. Match by intention (category name)
        candidates = Job.objects.filter(audit_status=1)
        
        if location:
            candidates = candidates.filter(location__icontains=location)
        if degree:
            candidates = candidates.filter(degree_requirement=degree)
        if job_type:
            candidates = candidates.filter(job_type=job_type)
        if nature:
            candidates = candidates.filter(company__nature=nature)
        
        results = []
        
        # Only fetch cold start logic if it's the first page or if we need more data
        # Cold start logic is simplified here: we just fetch more candidates if needed
        # But for simplicity in this hybrid system, we will just use a large candidate pool for cold start
        # and slice it manually for pagination.
        
        # Strategy: Build a large list of IDs then slice.
        # But for efficiency, we can chain querysets.
        
        # A. Job Intention
        qs1 = Job.objects.none()
        if job_intention:
            qs1 = candidates.filter(
                Q(job_category__name__icontains=job_intention) | 
                Q(job_name__icontains=job_intention)
            )
            
        # B. Major
        qs2 = Job.objects.none()
        if major:
             qs2 = candidates.filter(
                Q(major__name__icontains=major) |
                Q(job_name__icontains=major)
            ).exclude(id__in=qs1.values('id'))
             
        # C. Popular
        qs3 = candidates.order_by('-deliveries_count', '-collections_count', '-views_count')\
            .exclude(id__in=qs1.values('id'))\
            .exclude(id__in=qs2.values('id'))
            
        # Combine manually (not ideal for large offsets but works for cold start)
        # Since union() has limitations with ordering in some DBs, let's fetch in order.
        # But wait, we need to support infinite scroll.
        # Let's simplify: Return Popular jobs with filters as the "infinite" source.
        
        # Optimized Cold Start for Infinite Scroll:
        # 1. First 20 items: Mix of Intention + Major
        # 2. After that: Popular jobs
        
        total_needed = offset + limit
        current_count = 0
        
        # 1. Intention (Priority 1)
        intention_jobs = []
        if job_intention:
            intention_jobs = list(qs1[:total_needed])
        
        # 2. Major (Priority 2)
        major_jobs = []
        if major:
            # We need enough to fill the gap
            needed_major = total_needed - len(intention_jobs)
            if needed_major > 0:
                major_jobs = list(qs2[:needed_major])
                
        # 3. Popular (Priority 3 - Infinite)
        popular_jobs = []
        needed_pop = total_needed - len(intention_jobs) - len(major_jobs)
        if needed_pop > 0:
            # We can use offset here for efficiency if we assume previous pages were filled by priority 1 & 2
            # But simpler is to just fetch top N and slice
            popular_jobs = list(qs3[:needed_pop])
            
        all_candidates = (intention_jobs + major_jobs + popular_jobs)
        
        # Slice for current page
        page_items = all_candidates[offset : offset + limit]
        
        # Format results
        for job in page_items:
            reason = "当前热门岗位"
            if job in intention_jobs:
                reason = "根据你的求职意向推荐"
            elif job in major_jobs:
                reason = "根据你的专业推荐"
                
            results.append(self._format_cold_start(job, reason))
                
        return Response({
            "strategy": "coldstart",
            "count": 1000, # Fake count for infinite scroll
            "next": f"?limit={limit}&offset={offset+limit}",
            "previous": None,
            "results": results
        })

    def _format_cold_start(self, job, reason_text):
        serializer = JobSerializer(job, context={'request': self.request})
        return {
            "job": serializer.data,
            "score_item": 0.0,
            "score_user": 0.0,
            "score_hybrid": 0.0,
            "reason": [{"type": "coldstart", "text": reason_text}],
            "update_time": None
        }
