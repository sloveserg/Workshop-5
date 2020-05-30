from django.core.exceptions import ValidationError
import re


def phone_number_validator(value):
    try:
        re.search(r'^\+?3?8?0[5-9][0-9]\d{7}$', value).group(0)
    except AttributeError as e:
        raise ValidationError("Phone number is not correct. Example: +380561972343")
