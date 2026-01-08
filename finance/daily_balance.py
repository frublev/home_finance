from datetime import timedelta, date
from collections import defaultdict
from decimal import Decimal
from .models import Account, Transaction, DailyBalance

class DailyBalanceService:
    @staticmethod
    def get_balance_on_date(account: Account, target_date: date) -> Decimal:
        """
        Возвращает баланс на конкретную дату и заполняет пропущенные дни.
        С учётом типа транзакции.
        """
        # ищем последний сохранённый баланс
        last = (
            DailyBalance.objects
            .filter(account=account, date__lte=target_date)
            .order_by("-date")
            .first()
        )

        if last:
            balance = last.balance
            start_date = last.date + timedelta(days=1)
        else:
            balance = Decimal(0)
            # если транзакций ещё не было, берём дату первой транзакции
            first_tx = Transaction.objects.filter(account=account).order_by("transaction_time").first()
            start_date = first_tx.transaction_time.date() if first_tx else target_date

        if start_date > target_date:
            # баланс уже есть на target_date
            return balance

        # получаем транзакции между start_date и target_date
        tx_qs = Transaction.objects.filter(
            account=account,
            transaction_time__date__gte=start_date,
            transaction_time__date__lte=target_date
        ).select_related('category')

        # группируем транзакции по дате и корректируем знак
        tx_by_day = defaultdict(list)
        for tx in tx_qs:
            tx_date = tx.transaction_time.date()
            amount = tx.amount
            tx_type = tx.type  # category.type
            if tx_type in ["Outcome", "Transfer_from"]:
                amount = -amount
            # Income и Transfer_to остаются положительными
            tx_by_day[tx_date].append(amount)

        # идём по дням и сохраняем баланс
        current_date = start_date
        while current_date <= target_date:
            if current_date in tx_by_day:
                balance += sum(tx_by_day[current_date])
            # сохраняем или обновляем дневной баланс
            DailyBalance.objects.update_or_create(
                account=account,
                date=current_date,
                defaults={"balance": balance},
            )
            current_date += timedelta(days=1)

        return balance

    @staticmethod
    def invalidate_from_date(account: Account, start_date: date):
        """
        Удаляет дневные балансы начиная с указанной даты.
        Используется при добавлении/редактировании/удалении транзакций.
        """
        DailyBalance.objects.filter(account=account, date__gte=start_date).delete()

    @staticmethod
    def recalc_all(account: Account):
        """
        Полный пересчёт всех дневных балансов для данного счета.
        """
        first_tx = Transaction.objects.filter(account=account).order_by("transaction_time").first()
        start_date = first_tx.transaction_time.date() if first_tx else date.today()
        DailyBalanceService.get_balance_on_date(account, date.today())
