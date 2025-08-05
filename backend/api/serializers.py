import base64

from django.contrib.auth import authenticate, get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.recipe_utils import create_recipe_ingredients
from ingredients.models import Ingredient
from recipes.models import Recipe, RecipeIngredientAmount, RecipeTags
from tags.models import Tag
from users import user_utils as us

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        ]
        extra_kwargs = {
            "email": {"required": True, "allow_blank": False},
            "username": {"required": True, "allow_blank": False},
            "first_name": {"required": True, "allow_blank": False},
            "last_name": {"required": True, "allow_blank": False},
            "password": {
                "required": True,
                "allow_blank": False,
                "write_only": True,
            },
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
        ]

    def get_is_subscribed(self, author):
        request = self.context.get("request")
        user = request.user if request else None
        if request and user.is_authenticated:
            return us.is_subscribed(user, author)
        return False


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")
        read_only_fields = ("id",)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")
        read_only_fields = ("id",)


class RecipeIngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.CharField(source="ingredient.name", required=False)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", required=False
    )
    amount = serializers.IntegerField(
        min_value=1,
        max_value=32000,
        error_messages={
            "min_value": "Количество ингредиента должно быть больше нуля.",
            "max_value": "Количество ингредиента не может превышать 32 000.",
        },
    )

    class Meta:
        model = RecipeIngredientAmount
        fields = ("id", "name", "measurement_unit", "amount")
        read_only_fields = ("name", "measurement_unit")

    def validate_id(self, value):
        if not Ingredient.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                f"Ингредиент с id {value} не найден."
            )
        return value


class RecipeTagsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="tag.id")
    name = serializers.CharField(source="tag.name", required=False)
    slug = serializers.SlugField(source="tag.slug", required=False)

    class Meta:
        model = RecipeTags
        fields = ("id", "name", "slug")
        read_only_fields = ("id",)


class RecipeSerializer(serializers.ModelSerializer):

    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = RecipeIngredientAmountSerializer(
        source="recipe_ingredients", many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(
        required=True,
        allow_null=True,
        error_messages={
            "required": "Обязательное поле.",
            "invalid_image": "Пожалуйста, загрузите валидное изображение.",
        },
    )
    cooking_time = serializers.IntegerField(
        min_value=1,
        max_value=32000,
        error_messages={
            "min_value": "Время приготовления должно быть больше нуля.",
            "max_value": "Время приготовления не может превышать 32000 минут.",
        },
    )

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = ("id",)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        tags_qs = instance.tags.all()
        representation["tags"] = TagSerializer(tags_qs, many=True).data
        return representation

    def get_is_favorited(self, recipe):
        user = self.context["request"].user
        if user.is_anonymous:
            return False
        return us.has_favorite(user, recipe)

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return us.has_in_cart(user, recipe)

    def validate_tags(self, tags):
        if not tags:
            raise ValidationError("Поле теги обязательно")
        tags_ids = [tag.id for tag in tags]
        if len(tags_ids) != len(set(tags_ids)):
            raise ValidationError("Теги должны быть уникальными.")
        for tag_id in tags_ids:
            if not Tag.objects.filter(id=tag_id).exists():
                raise ValidationError(f"Тег с id {tag_id} не найден.")
        return tags

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise ValidationError("Поле обязательно")
        ingredients_ids = [
            ingredient["ingredient"]["id"] for ingredient in ingredients
        ]
        if len(ingredients_ids) != len(set(ingredients_ids)):
            raise ValidationError("Ингредиенты должны быть уникальными.")
        return super().validate(ingredients)

    def create(self, validated_data):
        ingredients_data = validated_data.pop("recipe_ingredients")
        tags_data = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        create_recipe_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop("tags", None)
        ingredients_data = validated_data.pop("recipe_ingredients", None)
        if not ingredients_data:
            raise serializers.ValidationError("Поле ингредиенты обязательно")
        if not tags_data:
            raise serializers.ValidationError("Поле теги обязательно")

        instance = super().update(instance, validated_data)

        if tags_data is not None:
            instance.tags.set(tags_data)

        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            create_recipe_ingredients(instance, ingredients_data)

        return instance


class RecipeShortSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class SubscriptionsSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
            "avatar",
        )

    def get_is_subscribed(self, author):
        request = self.context.get("request")
        user = request.user if request else None
        if request and user.is_authenticated:
            return us.is_subscribed(user, author)
        return False

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes_limit = (
            request.query_params.get("recipes_limit") if request else None
        )
        recipes_qs = obj.recipes.all()
        if recipes_limit and str(recipes_limit).isdigit():
            recipes_qs = recipes_qs[: int(recipes_limit)]
        return RecipeShortSerializer(
            recipes_qs, many=True, context=self.context
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(
        required=True,
        allow_null=True,
        error_messages={
            "required": "Обязательное поле.",
            "invalid_image": "Пожалуйста, загрузите валидное изображение.",
        },
    )

    class Meta:
        model = User
        fields = ["avatar"]

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get("avatar", instance.avatar)
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        if email and password:
            user = authenticate(
                request=self.context.get("request"),
                username=email,
                password=password,
            )
            if not user:
                raise serializers.ValidationError(
                    "Невозможно войти с предоставленными учетными данными."
                )
        else:
            raise serializers.ValidationError("Введите email и пароль.")
        data["user"] = user
        return data


class SubscriptionActionSerializer(serializers.Serializer):
    target_user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
    )

    def validate(self, data):
        request_method = self.context.get("request").method
        user = self.context["request"].user
        target_user = data["target_user"]
        if request_method == "POST":
            if user == target_user:
                raise serializers.ValidationError(
                    "Нельзя подписаться на себя."
                )
            if us.is_subscribed(user, target_user):
                raise serializers.ValidationError(
                    "Вы уже подписаны на этого пользователя."
                )
        elif request_method == "DELETE":
            if user == target_user:
                raise serializers.ValidationError(
                    "Нельзя отписаться от самого себя."
                )
            if not us.is_subscribed(user, target_user):
                raise serializers.ValidationError(
                    "Вы не подписаны на этого пользователя."
                )
        return data


class FavoriteActionSerializer(serializers.Serializer):
    target_recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        write_only=True,
    )

    def validate(self, data):
        request_method = self.context.get("request").method
        user = self.context["request"].user
        target_recipe = data["target_recipe"]
        if request_method == "POST":
            if us.is_favorite(user, target_recipe):
                raise serializers.ValidationError(
                    "Этот рецепт уже в избранном."
                )
        elif request_method == "DELETE":
            if not us.is_favorite(user, target_recipe):
                raise serializers.ValidationError(
                    "Этот рецепт не в избранном."
                )
        return data


class CartActionSerializer(serializers.Serializer):
    target_recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        write_only=True,
    )

    def validate(self, data):
        request_method = self.context.get("request").method
        user = self.context["request"].user
        target_recipe = data["target_recipe"]
        if request_method == "POST":
            if us.has_in_cart(user, target_recipe):
                raise serializers.ValidationError(
                    "Этот рецепт уже в корзине покупок."
                )
        elif request_method == "DELETE":
            if not us.has_in_cart(user, target_recipe):
                raise serializers.ValidationError(
                    "Этот рецепт не в корзине покупок."
                )
        return data
