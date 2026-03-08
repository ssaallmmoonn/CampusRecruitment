from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import JobViewSet, DashboardViewSet

router = SimpleRouter()
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'', JobViewSet, basename='job')

urlpatterns = [
    path('', include(router.urls)),
]
