import hashlib
from django.conf import settings


def md5(data_string):

    obj = hashlib.md5(settings.SECRET_KEY.encode("utf_8"))
    obj.update(data_string.encode("utf_8"))
    return obj.hexdigest()
