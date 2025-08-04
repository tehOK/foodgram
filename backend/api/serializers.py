import base64
from django.core.files.base import ContentFile
from django.contrib.auth import authenticate, get_user_model

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from tags.models import Tag
from ingredients.models import Ingredient
from recipes.models import Recipe, RecipeIngredientAmount, RecipeTags
from users.models import Subscription

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

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                subscriber=request.user, author=obj
            ).exists()
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

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Количество ингредиента должно быть больше нуля."
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
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return user.has_favorite(recipe)

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return user.has_in_cart(recipe)

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

    def validate_cooking_time(self, cooking_time):
        if cooking_time <= 0:
            raise ValidationError(
                "Время приготовления должно быть больше нуля."
            )
        return cooking_time

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
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data["ingredient"]["id"]
            amount = ingredient_data["amount"]
            ingredient_instance = Ingredient.objects.get(id=ingredient_id)
            RecipeIngredientAmount.objects.create(
                recipe=recipe, ingredient=ingredient_instance, amount=amount
            )
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

            for ingredient_data in ingredients_data:
                ingredient_id = ingredient_data["ingredient"]["id"]
                amount = ingredient_data["amount"]
                ingredient_instance = Ingredient.objects.get(id=ingredient_id)
                RecipeIngredientAmount.objects.create(
                    recipe=instance,
                    ingredient=ingredient_instance,
                    amount=amount,
                )

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

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                subscriber=request.user, author=obj
            ).exists()
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


# class ShoppingCartListSerializer(serializers.ModelSerializer):
#     id = serializers.IntegerField(read_only=True)
#     name = serializers.CharField(read_only=True)
#     image = serializers.ImageField(read_only=True)
#     cooking_time = serializers.IntegerField(read_only=True)

#     class Meta:
#         model = Recipe
#         fields = ("id", "name", "image", "cooking_time")


# class ChangePasswordSerializer(serializers.Serializer):

#     new_password = serializers.CharField(write_only=True)
#     current_password = serializers.CharField(write_only=True)

#     def validate_current_password(self, value):
#         user = self.context["request"].user
#         if not user.check_password(value):
#             raise serializers.ValidationError("Неверный текущий пароль.")
#         return value

#     def save(self):
#         user = self.context["request"].user
#         user.set_password(self.validated_data["new_password"])
#         user.save()
