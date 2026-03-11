from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import ResumeViewSet, JobApplicationViewSet, BehaviorViewSet, ChatMessageViewSet

router = SimpleRouter()
router.register(r'resumes', ResumeViewSet, basename='resume')
router.register(r'applications', JobApplicationViewSet, basename='job-application')
router.register(r'behaviors', BehaviorViewSet, basename='behavior')
router.register(r'messages', ChatMessageViewSet, basename='chat-message')

urlpatterns = [
    path('', include(router.urls)),
]
