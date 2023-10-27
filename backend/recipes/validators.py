from django.core.exceptions import ValidationError


def validate_time(value):
    if value < 1:
        raise ValidationError(f'{value} меньше 1!')
