from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import JobViewSet, DashboardViewSet, JobCategoryViewSet, MajorCategoryViewSet, JobCategoryAdminViewSet, MajorCategoryAdminViewSet

router = SimpleRouter()
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'categories', JobCategoryViewSet, basename='job-category')
router.register(r'majors', MajorCategoryViewSet, basename='major-category')
router.register(r'admin/categories', JobCategoryAdminViewSet, basename='admin-job-category')
router.register(r'admin/majors', MajorCategoryAdminViewSet, basename='admin-major-category')
router.register(r'', JobViewSet, basename='job')

urlpatterns = [
    path('', include(router.urls)),
]
