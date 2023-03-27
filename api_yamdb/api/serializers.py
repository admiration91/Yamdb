from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator

from reviews import models
from reviews.models import Review, Title, User
from .validators import username_validation, year_validation


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели User."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )

    def validate_username(self, value):
        return username_validation(value)


class UserRestrictedSerializer(UserSerializer):
    """Сериализатор модели User для изменения пользователями их аккаунтов."""
    username = serializers.CharField(
        required=True,
        max_length=settings.USERNAME_MAX_LENGTH,
        validators=[
            username_validation,
        ])
    email = serializers.EmailField(
        required=True,
        max_length=settings.EMAIL_MAX_LENGTH,
        validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta(UserSerializer.Meta):
        read_only_fields = ('username', 'email', 'role')


class SignUpSerializer(serializers.Serializer):
    """Сериализатор регистрации нового пользователя."""
    username = serializers.CharField(
        required=True,
        max_length=settings.USERNAME_MAX_LENGTH,
        validators=[
            username_validation,
        ]
    )
    email = serializers.EmailField(
        max_length=settings.EMAIL_MAX_LENGTH,
        required=True,
    )


class GetJWTTokenSerializer(serializers.Serializer):
    """Сериализатор получения JWT токена."""
    username = serializers.CharField(
        required=True,
        validators=[
            username_validation
        ]
    )
    confirmation_code = serializers.CharField(
        required=True,
        max_length=254
    )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = models.Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = models.Genre


class TitleSerializer(serializers.ModelSerializer):
    genre = SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=models.Genre.objects.all()
    )
    category = SlugRelatedField(
        required=True,
        slug_field='slug',
        queryset=models.Category.objects.all()
    )

    class Meta:
        fields = '__all__'
        model = models.Title

    def validate_year(self, year):
        return year_validation(year)


class TitleGetSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField(
        source='reviews__score__avg', read_only=True
    )

    class Meta:
        fields = '__all__'
        model = models.Title


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = models.Comment
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True
    )

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if request.method == 'POST':
            if Review.objects.filter(title=title, author=author).exists():
                raise ValidationError('Нельзя добавлять более одного отзыва')
        return data

    class Meta:
        model = models.Review
        fields = '__all__'
