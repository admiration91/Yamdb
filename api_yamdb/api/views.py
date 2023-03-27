from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from reviews import models
from reviews.models import User

from .filters import TitleFilter
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsAuthorModeratorAdminOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, GetJWTTokenSerializer,
                          ReviewSerializer, SignUpSerializer,
                          TitleGetSerializer, TitleSerializer,
                          UserRestrictedSerializer, UserSerializer)
from .utils import send_confirmation_code


class UserViewSet(viewsets.ModelViewSet):
    """
    Вьюсет модели User.
    Пользователь может просматривать и редактировать только свой аккаунт.
    Администратор имеет полный доступ ко всем аккаунтам.
    """
    queryset = User.objects.get_queryset().order_by('username')
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']
    lookup_field = 'username'
    filter_backends = [filters.SearchFilter]
    search_fields = ('username',)
    pagination_class = PageNumberPagination

    @action(
        methods=('get', 'patch'),
        detail=False, url_path='me',
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        """Просмотр и изменение своего аккаунта."""
        serializer = UserRestrictedSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        if request.method == 'PATCH':
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class SignUpView(APIView):
    """
    Создание нового пользователя, если он не был создан ранее.
    Отправка кода для подтверждения регистрации на email пользователя.
    """
    permission_classes = [AllowAny]
    pagination_class = None

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')

        try:
            user, _ = User.objects.get_or_create(
                username=username,
                email=email
            )
        except IntegrityError as error:
            if 'username' in str(error):
                return Response(
                    {'username':
                     'Пользователь с этим username уже зарегистрирован'},
                    status=status.HTTP_400_BAD_REQUEST)
            elif 'email' in str(error):
                return Response(
                    {'email':
                     'Пользователь с этим email уже зарегистрирован'},
                    status=status.HTTP_400_BAD_REQUEST)
            else:
                raise IntegrityError(
                    ('Ошибка при создании новой записи в БД')
                ) from error

        user.confirmation_code = default_token_generator.make_token(user)
        user.save()
        send_confirmation_code(user)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class GetJWTTokenView(APIView):
    """
    Получение JWT токена при предоставлении username и confirmation_code.
    """
    permission_classes = [AllowAny]
    pagination_class = None

    def post(self, request):
        serializer = GetJWTTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data['confirmation_code']
        user = get_object_or_404(User, username=username)
        if user.confirmation_code != confirmation_code:
            return Response(
                {"confirmation_code": ("Неверный код доступа "
                                       f"{confirmation_code}")},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {
                "token": str(RefreshToken.for_user(user).access_token)
            }
        )


class TitleViewSet(viewsets.ModelViewSet):
    queryset = models.Title.objects.all().annotate(
        Avg("reviews__score")
    ).order_by("name")
    pagination_class = LimitOffsetPagination
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleGetSerializer
        else:
            return TitleSerializer

    def perform_create(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        instance_serializer = TitleGetSerializer(instance)
        return Response(
            instance_serializer.data,
            status=status.HTTP_201_CREATED
        )


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = models.Category.objects.all()
    pagination_class = LimitOffsetPagination
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = [IsAdminOrReadOnly]


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = models.Genre.objects.all()
    pagination_class = LimitOffsetPagination
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = [IsAdminOrReadOnly]


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorModeratorAdminOrReadOnly]

    def get_queryset(self):
        title = get_object_or_404(models.Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(models.Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorModeratorAdminOrReadOnly]

    def get_queryset(self):
        review = get_object_or_404(
            models.Review,
            pk=self.kwargs.get('review_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(models.Review, id=review_id, title=title_id)
        serializer.save(author=self.request.user, review=review)

    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
