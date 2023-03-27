import django_filters

from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    genre = django_filters.Filter(
        field_name="genre__slug",
        lookup_expr='iexact'
    )
    category = django_filters.Filter(
        field_name="category__slug",
        lookup_expr='iexact'
    )
    name = django_filters.Filter(
        field_name='name',
        lookup_expr='contains'
    )
    year = django_filters.Filter(
        field_name='year',
        lookup_expr='iexact'
    )

    class Meta:
        fields = '__all__'
        model = Title
