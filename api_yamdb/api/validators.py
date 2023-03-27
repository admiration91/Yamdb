import datetime
import re

from rest_framework.serializers import ValidationError


def username_validation(value):
    """
    Проверяет имя пользователя на запрещенные значения и знаки.
    """
    if value.lower() == 'me':
        raise ValidationError('Нельзя использовать "me" как имя пользователя')

    checked_value = re.match('^[\\w.@+-]+', value)
    if checked_value is None or checked_value.group() != value:
        if checked_value is None:
            forbidden_simbol = value[0]
        else:
            forbidden_simbol = value[checked_value.span()[1]]
        raise ValidationError(f'Нельзя использовать символ {forbidden_simbol} '
                              'в username. Имя пользователя может содержать '
                              'только буквы, цифры и символы @ . + - _.')
    return value


def year_validation(year):
    today = datetime.datetime.now()
    if today.year < year:
        raise ValidationError(
            'Год выпуска произведения не может быть больше текущего'
        )
    return year
