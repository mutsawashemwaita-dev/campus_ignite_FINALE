from django.apps import AppConfig


def _fix_context_copy():
    """Django 4.2 on Python 3.14: copying a template Context crashes with
    "'super' object has no attribute 'dicts'", which breaks the Django admin's
    add pages. This is the same repair newer Django versions made."""
    from copy import copy
    from django.template.context import BaseContext

    def __copy__(self):
        duplicate = BaseContext()
        duplicate.__class__ = self.__class__
        duplicate.__dict__ = copy(self.__dict__)
        duplicate.dicts = self.dicts[:]
        return duplicate

    BaseContext.__copy__ = __copy__


class EvangelismConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.evangelism'

    def ready(self):
        _fix_context_copy()