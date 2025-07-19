from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import IngredientViewSet, TagViewSet, UserViewSet
from api.serializers import UserSerializer


router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),  # For authentication
]