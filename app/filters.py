import django_filters
from .models import Medicine


class MedicineFilter(django_filters.FilterSet):
    category = django_filters.UUIDFilter(field_name="category__id")
    active_ingredient = django_filters.UUIDFilter(field_name="active_ingredients__id")

    class Meta:
        model = Medicine
        fields = ['category', 'active_ingredient']