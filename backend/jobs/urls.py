from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import JobViewSet

router = SimpleRouter()
router.register(r'', JobViewSet, basename='job')

urlpatterns = [
    path('', include(router.urls)),
]
