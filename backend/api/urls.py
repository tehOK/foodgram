from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import UserViewSet
from api.serializers import UserSerializer


router = DefaultRouter()
router.register(r'users', UserViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),  # For authentication
]