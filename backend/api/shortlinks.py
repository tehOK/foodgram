from django.shortcuts import get_object_or_404, redirect

from recipes.models import Recipe


def redirect_short_link(request, code):
    recipe = get_object_or_404(Recipe, slug=code)
    url = request.build_absolute_uri(f"/api/recipes/{recipe.id}/")
    return redirect(url)
