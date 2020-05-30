from .models import Category


def get_categories(request):
    """
    Используем context_processors, потому-что категории отображается всегда на navbar-e на любой странице
    Используем, чтобы не дублировать код в views.py
    :param request:
    :return: Список категорий
    """
    return {'categories': Category.objects.all()}
