from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter
from .views import RegisterView, MyTokenObtainPairView, UserProfileView, CompanyPublicView, ChangePasswordView, AdminViewSet, CompanyViewSet, StudentViewSet, IndustryViewSet

router = DefaultRouter()
router.register(r'admins', AdminViewSet, basename='admins')
router.register(r'companies', CompanyViewSet, basename='companies')
router.register(r'students', StudentViewSet, basename='students')
router.register(r'industries', IndustryViewSet, basename='industries')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('companies/<int:id>/', CompanyPublicView.as_view(), name='company-detail'),
    path('', include(router.urls)),
]
