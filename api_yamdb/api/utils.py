from django.conf import settings
from django.core.mail import send_mail


def send_confirmation_code(user):
    """
    Отправляет код подтверждения, необходимый для регистрации на почту.
    """
    send_mail(
        subject='Регистрация на Yamdb',
        message=(
            'Чтобы завершить регистрацию на Yamdb и получить токен отправьте '
            f'запрос с именем пользователя (username) {user.username} и '
            f'кодом подтверждения (confirmation_code) {user.confirmation_code}'
            ' на эндпойнт /api/v1/auth/token/.'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email]
    )
