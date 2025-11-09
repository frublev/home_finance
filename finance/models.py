from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Account(models.Model):
    CURRENCY_CHOICES = [
        ('EUR', 'Euro'),
        ('USD', 'US Dollar'),
        ('GBP', 'British Pound'),
        ('CZK', 'Czech Koruna'),
        ('PLN', 'Polish Zloty'),
        ('HUF', 'Hungarian Forint'),
    ]

    name = models.CharField(max_length=100, unique=True)  # Название счета
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Текущий баланс
    default = 'EUR'
    currency = models.CharField(
        max_length=10,
        choices=CURRENCY_CHOICES,
        default='EUR'
    )  # Валюта счета
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    datetime = models.DateTimeField(auto_now_add=True)
    iban = models.CharField(max_length=24, unique=True, null=True, blank=True)

    class Meta:
        ordering = ['name']  # <-- сортировка по алфавиту

    def __str__(self):
        return f"{self.name} ({self.currency})"

    @property
    def currency_symbol(self):
        symbols = {
            'EUR': '€',
            'USD': '$',
            'GBP': '£',
            'CZK': 'Kč',
            'PLN': 'zł',
            'HUF': 'Ft',
        }
        return symbols.get(self.currency, self.currency)

class Category(models.Model):
    TYPE_CHOICES = [
        ('Income', 'Income'),
        ('Outcome', 'Outcome'),
        ('Transfer_from', 'Transfer_from'),  # транзакция списания
        ('Transfer_to', 'Transfer_to'),  # транзакция зачисления
    ]
    name = models.CharField(max_length=100, unique=True)  # Название категории
    description = models.TextField(max_length=1000, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='subcategories')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='Outcome'
    )
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_time = models.DateTimeField(default=timezone.now)
    datetime = models.DateTimeField(auto_now_add=True)
    description = models.TextField(max_length=1000, blank=True)
    category = models.ForeignKey("Category", on_delete=models.PROTECT)
    transfer_id = models.UUIDField(null=True, blank=True, db_index=True)

    # обязательное поле — всегда должен быть счёт
    account = models.ForeignKey("Account", on_delete=models.CASCADE)

    # кто именно внёс транзакцию в систему
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,   # удалили юзера — запись осталась
        null=True,
        blank=True,
        related_name="entered_transactions"
    )

    def __str__(self):
        return f"{self.amount} on {self.account} by {self.user}"

    @property
    def type(self):
        return self.category.type if self.category else None
