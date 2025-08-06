from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import TokenCreateView, UserViewSet
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.pagination import FoodgramRecipePagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    AvatarSerializer,
    CartActionSerializer,
    FavoriteActionSerializer,
    IngredientSerializer,
    LoginSerializer,
    RecipeSerializer,
    RecipeShortSerializer,
    SubscriptionActionSerializer,
    SubscriptionsSerializer,
    TagSerializer,
)
from ingredients.models import Ingredient
from recipes.models import Recipe, RecipeIngredientAmount
from tags.models import Tag
from users import user_utils as us

User = get_user_model()


class FoodgramUserViewSet(UserViewSet):

    def get_permissions(self):
        if self.action in ["retrieve", "list", "create"]:
            permission_classes = (permissions.AllowAny,)
        else:
            permission_classes = (permissions.IsAuthenticated,)
        return [permission() for permission in permission_classes]

    @action(
        detail=False,
        methods=("put", "delete"),
        url_path="me/avatar",
        permission_classes=(permissions.IsAuthenticated,),
    )
    def set_avatar(self, request):
        user = request.user
        if request.method == "DELETE":
            user.avatar.delete(save=False)
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = AvatarSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(
        detail=True,
        methods=("post", "delete"),
        url_path="subscribe",
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscribe(self, request, id=None):
        user = request.user
        target_user = get_object_or_404(User, id=id)
        serializer = SubscriptionActionSerializer(
            data={"target_user": id}, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        if request.method == "POST":
            us.subscribe(user, target_user)
            response_serializer = SubscriptionsSerializer(
                target_user, context={"request": request}
            )
            return Response(
                response_serializer.data, status=status.HTTP_201_CREATED
            )

        elif request.method == "DELETE":
            us.unsubscribe(user, target_user)
            return Response(
                {"detail": "Вы успешно отписались от пользователя."},
                status=status.HTTP_204_NO_CONTENT,
            )


class SubscriptionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = SubscriptionsSerializer

    def get_queryset(self):
        user = self.request.user
        subscriptions = us.all_subscriptions(user)
        authors = [sub.author for sub in subscriptions]
        return authors


class FoodgramTokenCreate(TokenCreateView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"auth_token": token.key})


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (SearchFilter,)
    pagination_class = None
    search_fields = ("name",)

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    lookup_field = "id"
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = FoodgramRecipePagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=("post", "delete"),
        url_path="favorite",
        serializer_class=RecipeShortSerializer,
    )
    def add_delete_in_favorite(self, request, id=None):
        recipe = get_object_or_404(Recipe, id=id)
        user = request.user
        serializer = FavoriteActionSerializer(
            data={"target_recipe": id}, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        if request.method == "POST":
            user.is_favorited.add(recipe)
            serializer = self.get_serializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            user.is_favorited.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=("get",),
        url_path="get-link",
    )
    def get_link(self, request, id=None):
        recipe = get_object_or_404(Recipe, id=id)
        slug = recipe.slug
        url = request.build_absolute_uri(f"/r/{slug}/")
        return Response({"short-link": url}, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=("post", "delete"),
        url_path="shopping_cart",
        serializer_class=RecipeShortSerializer,
    )
    def add_delete_in_cart(self, request, id=None):
        recipe = get_object_or_404(Recipe, id=id)
        user = request.user
        serializer = CartActionSerializer(
            data={"target_recipe": id}, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        if request.method == "POST":
            user.is_in_shopping_cart.add(recipe)
            serializer = self.get_serializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == "DELETE":
            user.is_in_shopping_cart.remove(recipe)
            return Response(
                status=status.HTTP_204_NO_CONTENT,
            )

    @action(
        detail=False,
        methods=("get",),
        url_path="download_shopping_cart",
    )
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart_items = user.is_in_shopping_cart.all()
        if not shopping_cart_items.exists():
            return Response(
                {"detail": "Ваш список покупок пуст."},
                status=status.HTTP_404_NOT_FOUND,
            )

        ingredient_amounts = RecipeIngredientAmount.objects.filter(
            recipe__in=shopping_cart_items
        ).select_related("ingredient")

        shopping_list = {}

        for item in ingredient_amounts:
            name = item.ingredient.name
            if name not in shopping_list:
                shopping_list[name] = {
                    "measurement_unit": item.ingredient.measurement_unit,
                    "amount": item.amount,
                }
            else:
                shopping_list[name]["amount"] += item.amount

        response_data = "\n".join(
            f"{name}: {data['amount']} {data['measurement_unit']}"
            for name, data in shopping_list.items()
        )

        response = Response(response_data, content_type="text/plain")
        response["Content-Disposition"] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response
