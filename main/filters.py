import django_filters
from django_filters.rest_framework import FilterSet

from main.models import Post


class ProductFilter(FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    description = django_filters.CharFilter(field_name='description', lookup_expr='icontains')

    class Meta:
        model = Post
        fields = ('category', 'title', 'description')