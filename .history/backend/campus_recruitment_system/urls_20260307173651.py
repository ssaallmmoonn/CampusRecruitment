from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    # path('api/jobs/', include('jobs.urls')),
    # path('api/recruitment/', include('recruitment.urls')),
    # path('api/recommendation/', include('recommendation.urls')),
]
