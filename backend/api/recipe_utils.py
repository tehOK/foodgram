from django.shortcuts import get_object_or_404, redirect

from ingredients.models import Ingredient
from recipes.models import Recipe, RecipeIngredientAmount


def create_recipe_ingredients(recipe, ingredients_data):
    objects = []
    for ingredient_data in ingredients_data:
        ingredient_id = ingredient_data["ingredient"]["id"]
        amount = ingredient_data["amount"]
        ingredient_instance = Ingredient.objects.get(id=ingredient_id)
        objects.append(
            RecipeIngredientAmount(
                recipe=recipe,
                ingredient=ingredient_instance,
                amount=amount,
            )
        )
    RecipeIngredientAmount.objects.bulk_create(objects)


def redirect_short_link(request, code):
    recipe = get_object_or_404(Recipe, slug=code)
    url = request.build_absolute_uri(f"/recipes/{recipe.id}/")
    return redirect(url)
