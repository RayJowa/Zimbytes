from .models import Category


def load_categories(request):
    categories = Category.objects.filter(deactivate=False)
    return {
        'categories': categories
    }

