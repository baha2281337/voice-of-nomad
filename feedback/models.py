from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    name = models.CharField(_('название'), max_length=100, unique=True)
    slug = models.SlugField(_('код'), max_length=100, unique=True)
    sort_order = models.PositiveSmallIntegerField(_('порядок сортировки'), default=0)
    is_active = models.BooleanField(_('активна'), default=True)

    class Meta:
        ordering = ('sort_order', 'name')
        verbose_name = _('категория')
        verbose_name_plural = _('категории')

    def __str__(self):
        return self.name


class Feedback(models.Model):
    class Kind(models.TextChoices):
        PROPOSAL = 'proposal', _('Предложение')
        PROBLEM = 'problem', _('Проблема')

    class Status(models.TextChoices):
        NEW = 'new', _('Новое')
        UNDER_REVIEW = 'under_review', _('На рассмотрении')
        ACCEPTED = 'accepted', _('Принято')
        IN_PROGRESS = 'in_progress', _('В работе')
        RESOLVED = 'resolved', _('Решено')
        REJECTED = 'rejected', _('Отклонено')

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='feedback_items',
        verbose_name=_('владелец обращения'),
    )
    category = models.ForeignKey(
        'feedback.Category',
        on_delete=models.PROTECT,
        related_name='feedback_items',
        verbose_name=_('категория'),
    )
    kind = models.CharField(_('тип обращения'), max_length=16, choices=Kind.choices)
    title = models.CharField(_('заголовок'), max_length=160)
    description = models.TextField(_('описание'))
    location = models.CharField(_('место'), max_length=160, blank=True)
    is_anonymous = models.BooleanField(_('анонимная публикация'), default=False)
    status = models.CharField(
        _('статус'),
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('дата обновления'), auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=('status', 'created_at'), name='feedback_status_created_idx'),
            models.Index(fields=('category', 'status'), name='feedback_category_status_idx'),
            models.Index(fields=('created_by', 'created_at'), name='feedback_owner_created_idx'),
        ]
        verbose_name = _('обращение')
        verbose_name_plural = _('обращения')

    def __str__(self):
        return self.title


class Attachment(models.Model):
    feedback = models.ForeignKey(
        Feedback,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name=_('обращение'),
    )
    file = models.FileField(_('файл'), upload_to='feedback/%Y/%m/')
    uploaded_at = models.DateTimeField(_('дата загрузки'), auto_now_add=True)

    class Meta:
        ordering = ('uploaded_at',)
        verbose_name = _('вложение')
        verbose_name_plural = _('вложения')

    def __str__(self):
        return self.file.name or f'Attachment {self.pk}'


class Vote(models.Model):
    feedback = models.ForeignKey(
        Feedback,
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name=_('обращение'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feedback_votes',
        verbose_name=_('пользователь'),
    )
    created_at = models.DateTimeField(_('дата голоса'), auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        constraints = [
            models.UniqueConstraint(
                fields=('feedback', 'user'),
                name='feedback_vote_user_uq',
            ),
        ]
        verbose_name = _('голос')
        verbose_name_plural = _('голоса')


class StatusHistory(models.Model):
    feedback = models.ForeignKey(
        Feedback,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name=_('обращение'),
    )
    previous_status = models.CharField(
        _('предыдущий статус'),
        max_length=20,
        choices=Feedback.Status.choices,
        blank=True,
    )
    new_status = models.CharField(
        _('новый статус'),
        max_length=20,
        choices=Feedback.Status.choices,
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='feedback_status_changes',
        null=True,
        blank=True,
        verbose_name=_('изменил'),
    )
    note = models.TextField(_('комментарий к изменению'), blank=True)
    changed_at = models.DateTimeField(_('дата изменения'), auto_now_add=True)

    class Meta:
        ordering = ('-changed_at',)
        indexes = [
            models.Index(fields=('feedback', 'changed_at'), name='feedback_history_date_idx'),
        ]
        verbose_name = _('изменение статуса')
        verbose_name_plural = _('история статусов')


class OfficialReply(models.Model):
    feedback = models.ForeignKey(
        Feedback,
        on_delete=models.CASCADE,
        related_name='official_replies',
        verbose_name=_('обращение'),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='official_replies',
        verbose_name=_('автор ответа'),
    )
    body = models.TextField(_('официальный ответ'))
    created_at = models.DateTimeField(_('дата ответа'), auto_now_add=True)
    updated_at = models.DateTimeField(_('дата обновления'), auto_now=True)

    class Meta:
        ordering = ('created_at',)
        verbose_name = _('официальный ответ')
        verbose_name_plural = _('официальные ответы')


class InternalNote(models.Model):
    feedback = models.ForeignKey(
        Feedback,
        on_delete=models.CASCADE,
        related_name='internal_notes',
        verbose_name=_('обращение'),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='feedback_internal_notes',
        verbose_name=_('автор заметки'),
    )
    body = models.TextField(_('внутренняя заметка'))
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('дата обновления'), auto_now=True)

    class Meta:
        ordering = ('created_at',)
        verbose_name = _('внутренняя заметка')
        verbose_name_plural = _('внутренние заметки')


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('получатель'),
    )
    feedback = models.ForeignKey(
        Feedback,
        on_delete=models.SET_NULL,
        related_name='notifications',
        null=True,
        blank=True,
        verbose_name=_('обращение'),
    )
    title = models.CharField(_('заголовок'), max_length=160)
    message = models.TextField(_('сообщение'))
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    read_at = models.DateTimeField(_('дата прочтения'), null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=('recipient', 'read_at', 'created_at'), name='notif_recipient_read_idx'),
        ]
        verbose_name = _('уведомление')
        verbose_name_plural = _('уведомления')
