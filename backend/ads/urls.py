from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import BannerViewSet, BrandViewSet

router = SimpleRouter()
router.register(r'banners', BannerViewSet, basename='banner')
router.register(r'brands', BrandViewSet, basename='brand')

urlpatterns = [
    path('', include(router.urls)),
]
