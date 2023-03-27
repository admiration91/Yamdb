from django.contrib import admin

from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget

from .models import (
    Category, Comment,
    Genre, GenreTitle,
    Title, Review
)


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        fields = (
            'id',
            'name',
            'slug',
        )


class CategoryAdmin(ImportExportModelAdmin):
    resource_class = CategoryResource
    list_display = (
        'id',
        'name',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('slug',)
    empty_value_display = '-пусто-'


class GenreResource(resources.ModelResource):
    class Meta:
        model = Genre
        fields = (
            'id',
            'name',
            'slug',
        )


class GenreAdmin(ImportExportModelAdmin):
    resource_class = GenreResource
    list_display = (
        'id',
        'name',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('slug',)
    empty_value_display = '-пусто-'


class GenreTitleResource(resources.ModelResource):
    class Meta:
        model = GenreTitle
        fields = (
            'id',
            'genre_id',
            'title_id',
        )


class GenreTitleAdmin(ImportExportModelAdmin):
    resource_class = GenreTitleResource
    list_display = (
        'id',
        'genre_id',
        'title_id',
    )


class TitleResource(resources.ModelResource):

    class Meta:
        model = Title
        exclude = ('genre', 'description',)


class TitleAdmin(ImportExportModelAdmin):
    resource_class = TitleResource
    list_display = (
        'id',
        'name',
        'year',
        'description',
        'category',
        'get_genre',
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('genre')

    def get_genre(self, obj):
        return [genre.name for genre in obj.genre.all()]


class ReviewResource(resources.ModelResource):
    title = Field(
        attribute='title',
        column_name='title_id',
        widget=ForeignKeyWidget(Title, 'id')
    )

    class Meta:
        model = Review


class ReviewAdmin(ImportExportModelAdmin):
    resource_class = ReviewResource
    list_display = (
        'id',
        'title',
        'text',
        'author',
        'score',
        'pub_date'
    )


class CommentResource(resources.ModelResource):
    rewiew = Field(
        attribute='review',
        column_name='review_id',
        widget=ForeignKeyWidget(Review, 'id')
    )

    class Meta:
        model = Comment


class CommentAdmin(ImportExportModelAdmin):
    resource_class = CommentResource
    list_display = (
        'id',
        'review',
        'text',
        'author',
        'pub_date'
    )


admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(GenreTitle, GenreTitleAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
