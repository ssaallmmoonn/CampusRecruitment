from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import RecommendationViewSet

router = SimpleRouter()
router.register('recommendations', RecommendationViewSet, basename='recommendations')

urlpatterns = [
    path('', include(router.urls)),
]
