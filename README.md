[![.github/workflows/yamdb_workflow.yml](https://github.com/admiration91/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)](https://github.com/admiration91/yamdb_final/actions/workflows/yamdb_workflow.yml)
# REST API для YaMDb

## Описание
Проект YaMDb собирает **отзывы** пользователей на **произведения**. Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.

Произведения делятся на **категории**, такие как «Книги», «Фильмы», «Музыка». Например, в категории «Книги» могут быть произведения «Винни-Пух и все-все-все» и «Марсианские хроники», а в категории «Музыка» — песня «Давеча» группы «Жуки» и вторая сюита Баха. Список категорий может быть расширен (например, можно добавить категорию «Изобразительное искусство» или «Ювелирка»).

Произведению может быть присвоен **жанр** из списка предустановленных (например, «Сказка», «Рок» или «Артхаус»).

Добавлять произведения, категории и жанры может только администратор.

Благодарные или возмущённые пользователи оставляют к произведениям текстовые **отзывы** и ставят произведению оценку в диапазоне от одного до десяти (целое число); из пользовательских оценок формируется усреднённая оценка произведения — **рейтинг** (целое число). На одно произведение пользователь может оставить только один отзыв.

Пользователи могут оставлять **комментарии** к отзывам.

Добавлять отзывы, комментарии и ставить оценки могут только аутентифицированные пользователи.

### Алгоритм регистрации пользователей
1. Пользователь отправляет POST-запрос на добавление нового пользователя с параметрами `email` и `username` на эндпоинт `/api/v1/auth/signup/`.
2. **YaMDB** отправляет письмо с кодом подтверждения (`confirmation_code`) на адрес `email`.
3. Пользователь отправляет POST-запрос с параметрами `username` и `confirmation_code` на эндпоинт `/api/v1/auth/token/`, в ответе на запрос ему приходит `token` (JWT-токен).
4. При желании пользователь отправляет PATCH-запрос на эндпоинт `/api/v1/users/me/` и заполняет поля в своём профайле (описание полей — в документации).

### Пользовательские роли
- **Аноним** — может просматривать описания произведений, читать отзывы и комментарии.
- **Аутентифицированный пользователь** (`user`) — может, как и **Аноним**, читать всё, дополнительно он может публиковать отзывы и ставить оценку произведениям (фильмам/книгам/песенкам), может комментировать чужие отзывы; может редактировать и удалять **свои** отзывы и комментарии. Эта роль присваивается по умолчанию каждому новому пользователю.
- **Модератор** (`moderator`) — те же права, что и у **Аутентифицированного пользователя** плюс право удалять **любые** отзывы и комментарии.
- **Администратор** (`admin`) — полные права на управление всем контентом проекта. Может создавать и удалять произведения, категории и жанры. Может назначать роли пользователям.
- **Суперюзер Django** — обладет правами администратора (`admin`)

### Самостоятельная регистрация новых пользователей
1.  Пользователь отправляет POST-запрос с параметрами `email` и `username` на эндпоинт `/api/v1/auth/signup/`.
2.  Сервис **YaMDB** отправляет письмо с кодом подтверждения (`confirmation_code`) на указанный адрес `email`.
3.  Пользователь отправляет POST-запрос с параметрами `username` и `confirmation_code` на эндпоинт `/api/v1/auth/token/`, в ответе на запрос ему приходит `token` (JWT-токен).

В результате пользователь получает токен и может работать с API проекта, отправляя этот токен с каждым запросом.

После регистрации и получения токена пользователь может отправить PATCH-запрос на эндпоинт `/api/v1/users/me/` и заполнить поля в своём профайле (описание полей — в документации).

## Используемые технологии и библиотеки
-   [Python >= 3.7](https://www.python.org/)
-   [Django = 3.2](https://www.djangoproject.com/)
-   [djangorestframework = 3.12.4](https://www.django-rest-framework.org/)
-   [djangorestframework-simplejwt = 4.7.2](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)
-   [djoser = 2.1.0](https://djoser.readthedocs.io/en/latest/getting_started.html)
-   [PyJWT = 2.1.0](https://pyjwt.readthedocs.io/)
-   [requests = 2.26.0](https://requests.readthedocs.io/en/latest/user/quickstart/)
-   [pytest = 6.2.4](https://docs.pytest.org/en/7.1.x/getting-started.html)
-   [pytest-django = 4.4.0](https://pytest-django.readthedocs.io/en/latest/tutorial.html)
-   [pytest-pythonpath = 0.7.3](https://pypi.org/project/pytest-pythonpath/)
-   [django-import-export = 3.0.2](https://django-import-export.readthedocs.io/en/latest/getting_started.html)
-   [django-filter = 22.1](https://django-filter.readthedocs.io/)
-   [gunicorn==20.0.4](https://docs.gunicorn.org/en/stable/settings.html)
-   [psycopg2-binary==2.8.6](https://www.psycopg.org/docs/)

При необходимости есть возможность наполнить БД данными из CSV файлов. Импорт осуществляется через панель администратора, с помощью кнопки импорт. Порядок импорта в таблицы: пользователи, жанры, категории, произведения, таблица связи genre titles, отзывы, комментарии.

## Документация
Документация находится по адресу `http://127.0.0.1:8000/redoc/`.


## Примеры запросов к API

#### Авторизация
Регистрация нового пользователя:
```POST
http://127.0.0.1:8000/api/v1/auth/signup/
```
payload:
```application/json
{
  "email": "user@example.com",
  "username": "string"
}
```

Получение JWT-токена:
```POST
http://127.0.0.1:8000/api/v1/auth/token/
```
payload:
```application/json
{
  "username": "string",
  "confirmation_code": "string"
}
```

#### Категории
Получение списка категорий:
```GET
http://127.0.0.1:8000/api/v1/categories/
```

#### Жанры
Получение списка жанров:
```GET
http://127.0.0.1:8000/api/v1/genres/
```

#### Произведения
Получение списка произведений:
```GET
http://127.0.0.1:8000/api/v1/titles/
```

Получение информации о произведении:
```GET
http://127.0.0.1:8000/api/v1/titles/{titles_id}/
```

#### Отзывы
Получение списка всех отзывов:
```GET
http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/
```

Добавление нового отзыва:
```POST
http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/
```
payload:
```application/json
{
  "text": "string",
  "score": 1
}
```

Полуение отзыва по id:
```GET
http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/{review_id}/
```

Частичное обновление отзыва по id:
```PATCH
http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/{review_id}/
```
payload:
```application/json
{
  "text": "string",
  "score": 1
}
```

Удаление отзыва по id:
```DELETE
http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/{review_id}/
```

#### Комментарии
Получение списка всех комментариев к отзыву:
```GET
http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/{review_id}/comments/
```

Добавление комментария к отзыву:
```POST
http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/{review_id}/comments/
```
payload:
```application/json
{
  "text": "string"
}
```

Получение комментария к отзыву:
```GET
http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/
```

Частичное обновление комментария к отзыву:
```PATCH
http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/
```
payload:
```application/json
{
  "text": "string"
}
```

Удаление комментария к отзыву:
```DELETE
http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/
```

### Разработчики:
- [lyapakin](https://github.com/lyapakin)
- [bearvar](https://github.com/bearvar)
- [admiration91](https://github.com/admiration91)