import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'student', _('Студент')
        MODERATOR = 'moderator', _('Модератор')
        ADMINISTRATOR = 'administrator', _('Администратор')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(
        _('роль'),
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )

    class Meta:
        verbose_name = _('пользователь')
        verbose_name_plural = _('пользователи')


class UserIdentity(models.Model):
    """Map an external account to an internal user without sharing its primary key."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='external_identities',
        verbose_name=_('пользователь'),
    )
    provider = models.SlugField(_('провайдер'), max_length=64)
    subject = models.CharField(_('внешний идентификатор'), max_length=255)
    created_at = models.DateTimeField(_('дата привязки'), auto_now_add=True)

    class Meta:
        verbose_name = _('внешняя учётная запись')
        verbose_name_plural = _('внешние учётные записи')
        constraints = [
            models.UniqueConstraint(
                fields=('provider', 'subject'),
                name='identity_provider_subject_uq',
            ),
        ]

    def __str__(self):
        return f'{self.provider} identity'
