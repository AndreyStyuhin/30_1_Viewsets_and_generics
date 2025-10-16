from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
import re

def validate_video_url(value):
    if not value:
        return
    url_validator = URLValidator()
    try:
        url_validator(value)
    except ValidationError:
        raise ValidationError("Некорректная ссылка.")
    if not re.match(r'^https?://(www\.)?(youtube\.com|youtu\.be)/', value):
        raise ValidationError("Разрешены только ссылки на YouTube.")