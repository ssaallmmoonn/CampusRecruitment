from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import BannerViewSet, BrandViewSet, NoticeViewSet

router = SimpleRouter()
router.register(r'banners', BannerViewSet, basename='banner')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'notices', NoticeViewSet, basename='notice')

urlpatterns = [
    path('', include(router.urls)),
]
