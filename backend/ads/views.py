from rest_framework import viewsets, permissions
from .models import Banner, Brand
from .serializers import BannerSerializer, BrandSerializer

class BannerViewSet(viewsets.ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        # Admin sees all, public sees only active
        if self.action == 'list':
            user = self.request.user
            # Check if user is admin (role 0)
            if user.is_authenticated and hasattr(user, 'role') and user.role == 0:
                return Banner.objects.all()
            return Banner.objects.filter(is_active=True)
        return super().get_queryset()

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        # Admin sees all, public sees only active
        if self.action == 'list':
            user = self.request.user
            # Check if user is admin (role 0)
            if user.is_authenticated and hasattr(user, 'role') and user.role == 0:
                return Brand.objects.all()
            return Brand.objects.filter(is_active=True)
        return super().get_queryset()
