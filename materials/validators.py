from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
import re


class YouTubeURLValidator:
    """
    Валидатор, который проверяет, является ли ссылка URL-адресом,
    ведущим на YouTube.
    """
    __fields__ = ('video_url',)

    def __call__(self, value):
        if not value:
            return
        url_validator = URLValidator()
        try:
            url_validator(value)
        except ValidationError:
            raise ValidationError("Некорректная ссылка.")
        if not re.match(r'^https?://(www\.)?(youtube\.com|youtu\.be)/.*', value):
            raise ValidationError("Разрешены только ссылки на YouTube.")