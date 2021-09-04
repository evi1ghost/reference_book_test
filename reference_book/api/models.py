# from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


WORK = 'work'
PERSONAL = 'personal'
FAX = 'fax'

PHONE_TYPES = [
    (WORK, 'Рабочий'),
    (PERSONAL, 'Личный'),
    (FAX, 'Факс'),
]


class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(_('username'), max_length=150, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Organization(models.Model):
    name = models.CharField(
        verbose_name='Наименование',
        max_length=200,
        unique=True
    )
    address = models.CharField(verbose_name='Адрес', max_length=200)
    description = models.TextField(verbose_name='Описание')
    owner = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='organization',
        verbose_name='Владелец'
    )
    modifiers = models.ManyToManyField(
        User,
        related_name='can_modify',
        verbose_name='Вправе вносить изменения',
        blank=True
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'<Organization: {self.name}>'

    class Meta:
        ordering = ['name']


class Employee(models.Model):
    name = models.CharField(verbose_name='ФИО', max_length=200)
    position = models.CharField(verbose_name='Должность', max_length=200)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='employees',
        verbose_name='Организация'
    )

    # todo: мешает работе админки - доработать или удалить
    # def clean(self):
    #     if len(self.phones.all()) == 0:
    #         raise ValidationError(
    #             'Должен быть указан как минимум один номер телефона.'
    #         )

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'<Employee: {self.name}>'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'organization'], name='unique_employee_name'
            ),
        ]


class Phone(models.Model):
    phone_type = models.CharField(
        verbose_name='Тип номера',
        choices=PHONE_TYPES,
        default=WORK,
        max_length=50
    )
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=(
            'Введите номер в формате: "+79161234567" (не более 15 цифр)'
        )
    )
    phone_number = models.CharField(
        verbose_name='Номер',
        max_length=16,
        validators=[phone_regex]
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='phones',
        verbose_name='Работник'
    )
