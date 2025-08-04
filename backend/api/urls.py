from django.urls import include, path
from djoser.views import TokenDestroyView
from rest_framework.routers import DefaultRouter

from api.views import (
    FoodgramTokenCreate,
    FoodgramUserViewSet,
    IngredientViewSet,
    RecipeViewSet,
    SubscriptionViewSet,
    TagViewSet,
)

router = DefaultRouter()
router.register("tags", TagViewSet, basename="tag")
router.register("ingredients", IngredientViewSet, basename="ingredient")
router.register("recipes", RecipeViewSet, basename="recipe")

user_patterns = [
    path(
        "<int:id>/",
        FoodgramUserViewSet.as_view({"get": "retrieve"}),
        name="user",
    ),
    path(
        "<int:id>/subscribe/",
        FoodgramUserViewSet.as_view(
            {"post": "subscribe", "delete": "subscribe"}
        ),
        name="subscribe",
    ),
    path(
        "me/", FoodgramUserViewSet.as_view({"get": "me"}), name="current_user"
    ),
    path(
        "set_password/",
        FoodgramUserViewSet.as_view({"post": "set_password"}),
        name="set_password",
    ),
    path(
        "me/avatar/",
        FoodgramUserViewSet.as_view(
            {"put": "set_avatar", "delete": "set_avatar"}
        ),
        name="avatar",
    ),
    path(
        "subscriptions/",
        SubscriptionViewSet.as_view({"get": "list"}),
        name="subscriptions",
    ),
    path(
        "",
        FoodgramUserViewSet.as_view({"get": "list", "post": "create"}),
        name="user_list",
    ),
]

auth_patterns = [
    path("token/login/", FoodgramTokenCreate.as_view(), name="token-login"),
    path("token/logout/", TokenDestroyView.as_view(), name="token-logout"),
]

urlpatterns = [
    path("auth/", include(auth_patterns)),
    path("users/", include(user_patterns)),
    path("", include(router.urls)),
]
