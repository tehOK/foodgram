def has_favorite(user, recipe):
    return user.is_favorited.filter(id=recipe.id).exists()


def has_in_cart(user, recipe):
    return user.is_in_shopping_cart.filter(id=recipe.id).exists()


def subscribe(user, target_user):
    return user.subscriptions.get_or_create(
        subscriber=user, author=target_user
    )


def unsubscribe(user, target_user):
    return user.subscriptions.filter(author=target_user).delete()


def is_subscribed(user, target_user):
    return user.subscriptions.filter(
        subscriber=user, author=target_user
    ).exists()


def is_favorite(user, recipe):
    return user.is_favorited.filter(id=recipe.id).exists()


def followers(user):
    return user.subscribers.filter(author=user)


def all_subscriptions(user):
    return user.subscriptions.all()


def favorited(user):
    return user.is_favorited.all()


def shopping_cart(user):
    return user.is_in_shopping_cart.all()
