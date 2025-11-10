import uuid
from decimal import Decimal

from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction as db_transaction

from datetime import datetime, timedelta, date
import calendar
from django.utils.timezone import now

from .forms import AccountForm, CategoryForm, TransactionForm, TransferForm
from .models import Account, Category, Transaction


@login_required
def home(request):
    return redirect('bank_and_cash')
    # return render(request, 'home.html')

@login_required
def create_account(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.created_by = request.user
            account.save()
            return redirect('bank_and_cash')
    else:
        form = AccountForm()
    return render(request, 'create_account.html', {'form': form})

@login_required
def bank_and_cash(request):
    # Показываем только счета текущего пользователя
    accounts = Account.objects.all()
    total_balance = accounts.aggregate(total=Sum('balance'))['total'] or 0
    return render(request, 'bank_and_cash.html', {'accounts': accounts, 'total_balance': total_balance})

@login_required
def account_detail(request, account_id):
    # Получаем счет или 404
    account = get_object_or_404(Account, id=account_id)

    if request.method == 'POST':
        form = AccountForm(request.POST, instance=account)
        print(request.POST)
        if form.is_valid():
            form.save()
            return redirect('bank_and_cash')  # после сохранения возвращаем на список счетов
        else:
            print(form.errors)
    else:
        form = AccountForm(instance=account)

    return render(request, 'account_detail.html', {
        'form': form,
        'account': account
    })

@login_required
def account_delete(request, account_id):
    account = get_object_or_404(Account, id=account_id)

    if request.method == 'POST':
        account.delete()
        messages.success(request, f'Account "{account.name}" has been deleted.')
        return redirect('bank_and_cash')

    # GET → показываем страницу подтверждения
    return render(request, 'account_confirm_delete.html', {'account': account})

@login_required
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.created_by = request.user
            category.save()
            return redirect('category')
    else:
        form = CategoryForm()
    return render(request, 'create_category.html', {'form': form})

@login_required
def category(request):
    categories = Category.objects.all()
    return render(request, 'category.html', {'categories': categories})

@login_required
def category_detail(request, category_id):
    category_ = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category_)
        print(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category')
        else:
            print(form.errors)
    else:
        form = CategoryForm(instance=category_)

    return render(request, 'category_detail.html', {
        'form': form,
        'category': category_
    })

@login_required
def category_delete(request, category_id):
    category_ = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        category_.delete()
        messages.success(request, f'Category "{category_.name}" has been deleted.')
        return redirect('category')

    return render(request, 'category_confirm_delete.html', {'category': category_})

@login_required
def all_transactions(request):
    filter_by = request.GET.get('filter', 'month')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    today = date.today()

    # Если даты не переданы, выставляем дефолт для фильтра
    if not from_date or not to_date:
        if filter_by == 'today':
            from_date = today
            to_date = today
        elif filter_by == 'week':
            from_date = today - timedelta(days=6)
            to_date = today
        elif filter_by == 'month':
            # предыдущий месяц
            prev_month = today.month - 1 or 12
            prev_year = today.year if today.month != 1 else today.year - 1
            days_in_prev_month = calendar.monthrange(prev_year, prev_month)[1]
            from_date = today - timedelta(days=days_in_prev_month - 1)
            to_date = today

    if isinstance(from_date, date):
        from_date_str = from_date.strftime('%Y-%m-%d')
    else:
        from_date_str = from_date or ''

    if isinstance(to_date, date):
        to_date_str = to_date.strftime('%Y-%m-%d')
    else:
        to_date_str = to_date or ''

    transactions = Transaction.objects.filter(
        transaction_time__date__gte=from_date if from_date else None,
        transaction_time__date__lte=to_date if to_date else None
    ).order_by('-transaction_time')

    account = request.GET.get('account', None)
    if account == 'None':
        account = None

    if account:
        account=int(account)
        transactions = transactions.filter(account=account)
        template_name = 'transaction/account_transactions.html'
    else:
        template_name = 'transaction/all_transactions.html'

    transaction_type = request.GET.get('type', None)
    if transaction_type == 'income':
        if account:
            transactions = transactions.filter(Q(category__type='Income') | Q(category__type='Transfer_to'))
        else:
            transactions = transactions.filter(category__type='Income')
    elif transaction_type == 'outcome':
        if account:
            transactions = transactions.filter(Q(category__type='Outcome') | Q(category__type='Transfer_from'))
        else:
            transactions = transactions.filter(category__type='Outcome')
    elif transaction_type == 'transfer':
        transactions = transactions.filter(Q(category__type='Transfer_from') | Q(category__type='Transfer_to'))
        # if account:
        #     transactions = transactions.filter(Q(category__type='Transfer_from') | Q(category__type='Transfer_to'))
        # else:
        #     transactions = transactions.filter(category__type='Transfer_from')
    else:
        transaction_type = 'None'

    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'transactions': page_obj,
        'from_date': from_date_str,
        'to_date': to_date_str,
        'active_filter': filter_by,
        'active_type': transaction_type,
        'account': int(account) if account else None,
    }

    return render(request, template_name, context)

@login_required
def income_list(request):
    transactions = Transaction.objects.filter(category__type="Income").order_by("-datetime")
    return render(request, "transaction/income_list.html", {"transactions": transactions})


@login_required
def outcome_list(request):
    transactions = Transaction.objects.filter(category__type="Outcome").order_by("-transaction_time")
    return render(request, "transaction/outcome_list.html", {"transactions": transactions})

@login_required

def transfer_list(request):
    """
    Выдаёт список переводов. Каждая пара транзакций объединяется по transfer_id.
    """
    # получаем все транзакции типа Transfer_from
    from_txs = Transaction.objects.filter(category__type="Transfer_from").order_by('-transaction_time')

    transfers = []
    for tx_from in from_txs:
        if not tx_from.transfer_id:
            continue  # пропускаем старые записи без transfer_id

        # ищем соответствующую зачисляющую транзакцию
        tx_to = Transaction.objects.filter(transfer_id=tx_from.transfer_id, category__type="Transfer_to").first()
        if not tx_to:
            continue  # на всякий случай

        transfers.append({
            "from_tx": tx_from,
            "to_tx": tx_to
        })

    return render(request, "transaction/transfer_list.html", {"transfers": transfers})

@login_required
def add_transaction(request, tx_type):
    if tx_type not in ["Income", "Outcome"]:
        return redirect("home")

    account_id = request.GET.get('account')

    if request.method == "POST":
        form = TransactionForm(request.POST, tx_type=tx_type)
        if form.is_valid():
            tx = form.save(commit=False)
            tx.user = request.user

            # Корректировка баланса
            if tx_type == "Income":
                tx.account.balance += tx.amount
            else:
                tx.account.balance -= tx.amount
            tx.account.save()

            tx.save()

            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect("all_transactions")

    else:
        if account_id:
            form = TransactionForm(tx_type=tx_type, initial={'account': account_id})
        else:
            form = TransactionForm(tx_type=tx_type)

    return render(request, "transaction/add_transaction.html", {
        "form": form,
        "tx_type": tx_type,
    })

@login_required
def add_transfer(request):
    account_id = request.GET.get('account')
    if request.method == "POST":
        form = TransferForm(request.POST)
        if form.is_valid():
            from_acc = form.cleaned_data["from_account"]
            to_acc = form.cleaned_data["to_account"]
            amount = form.cleaned_data["amount"]
            category_from = Category.objects.get(type="Transfer_from")
            category_to = Category.objects.get(type="Transfer_to")
            description = form.cleaned_data["description"]
            transaction_time = form.cleaned_data.get("transaction_time", timezone.now())
            transfer_id = uuid.uuid4()  # общий ID для пары транзакций

            with db_transaction.atomic():
                # списание
                tx_from = Transaction.objects.create(
                    amount=amount,
                    account=from_acc,
                    category=category_from,
                    description=f"Transfer to {to_acc.name}. {description}",
                    user=request.user,
                    transaction_time=transaction_time,
                    transfer_id=transfer_id,
                )
                from_acc.balance -= amount
                from_acc.save()

                # зачисление
                tx_to = Transaction.objects.create(
                    amount=amount,
                    account=to_acc,
                    category=category_to,
                    description=f"Transfer from {from_acc.name}. {description}",
                    user=request.user,
                    transaction_time=transaction_time,
                    transfer_id=transfer_id,
                )
                to_acc.balance += amount
                to_acc.save()

            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect("all_transactions")

            # return redirect("transfer_list")
    else:
        if account_id:
            form = TransferForm(initial={'from_account': account_id})
        else:
            form = TransferForm()

    # else:
    #     form = TransferForm()

    return render(request, "transaction/add_transfer.html", {"form": form})

@login_required
def edit_transaction(request, pk):
    tx = get_object_or_404(Transaction, pk=pk)

    # Если это перевод — редиректим (или рендерим) отдельную форму
    if tx.category and tx.category.type.lower() == "transfer":
        return edit_transfer(request, tx.transfer_id)

    # Сохраняем старые значения ДО создания формы (важно)
    old_amount = tx.amount
    old_account = tx.account
    old_type = tx.category.type if tx.category else None

    if request.method == "POST":
        form = TransactionForm(request.POST, instance=tx)
        if form.is_valid():
            with db_transaction.atomic():
                # Получаем новые значения (не сохраняем пока)
                new_tx = form.save(commit=False)
                new_amount = new_tx.amount
                new_account = new_tx.account
                new_type = new_tx.category.type if new_tx.category else None

                # Преобразуем в Decimal (страховка)
                old_amount = Decimal(old_amount)
                new_amount = Decimal(new_amount)

                # вычисляем "эффект" транзакции:
                # income => +amount, outcome => -amount
                def effect(amount, typ):
                    if typ == "Income" or typ == "income":
                        return Decimal(amount)
                    elif typ == "Outcome" or typ == "outcome":
                        return -Decimal(amount)
                    else:
                        return Decimal(0)  # для Transfer или незаданных категорий

                old_effect = effect(old_amount, old_type)
                new_effect = effect(new_amount, new_type)

                if old_account == new_account:
                    # если счёт не поменялся — просто применяем разницу
                    delta = new_effect - old_effect
                    if delta != 0:
                        old_account.balance = old_account.balance + delta
                        old_account.save()
                else:
                    # счёт поменялся — откатываем старый эффект с old_account
                    old_account.balance = old_account.balance - old_effect
                    old_account.save()

                    # и применяем новый эффект на new_account
                    new_account.balance = new_account.balance + new_effect
                    new_account.save()

                # Наконец сохраняем транзакцию
                new_tx.save()

            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect("all_transactions")

            # # Редирект на соответствующий список (по типу новой/текущей категории)
            # if new_type and (new_type.lower() == "transfer" or new_type == "Transfer"):
            #     return redirect("transfer_list")
            # elif new_type and (new_type.lower() == "income" or new_type == "Income"):
            #     return redirect("income_list")
            # else:
            #     return redirect("outcome_list")

    else:
        form = TransactionForm(instance=tx)

    return render(request, "transaction/edit_transaction.html", {"form": form, "transaction": tx})


@login_required
def edit_transfer(request, transfer_id):
    # Получаем обе части перевода
    tx_from = get_object_or_404(Transaction, transfer_id=transfer_id, category__type="Transfer_from")
    tx_to = get_object_or_404(Transaction, transfer_id=transfer_id, category__type="Transfer_to")

    # Сохраняем старые значения (до любых изменений)
    old_from_acc = tx_from.account
    old_to_acc = tx_to.account
    old_amount = Decimal(tx_from.amount)

    if request.method == "POST":
        form = TransferForm(request.POST)
        if form.is_valid():
            # Получаем новые данные из формы
            new_from_acc = form.cleaned_data["from_account"]
            new_to_acc = form.cleaned_data["to_account"]
            new_amount = Decimal(form.cleaned_data["amount"])
            # new_category = form.cleaned_data["category"]
            new_description = form.cleaned_data["description"]
            new_time = form.cleaned_data["transaction_time"]

            with db_transaction.atomic():
                # 1️⃣ Откатываем старый перевод
                old_from_acc.balance += old_amount
                old_from_acc.save(update_fields=["balance"])

                old_to_acc.balance -= old_amount
                old_to_acc.save(update_fields=["balance"])

                # 2️⃣ Применяем новые изменения
                if new_from_acc == old_from_acc:
                    new_from_acc.balance += (old_amount - new_amount)
                elif new_from_acc == old_to_acc:
                    new_from_acc.balance -= (old_amount + new_amount)
                else:
                    new_from_acc.balance -= new_amount
                new_from_acc.save(update_fields=["balance"])

                if new_to_acc == old_to_acc:
                    new_to_acc.balance -= (old_amount - new_amount)
                elif new_to_acc == old_from_acc:
                    new_to_acc.balance += (old_amount + new_amount)
                else:
                    new_to_acc.balance += new_amount
                new_to_acc.save(update_fields=["balance"])

                # 3️⃣ Обновляем обе транзакции
                tx_from.account = new_from_acc
                tx_from.amount = new_amount
                tx_from.category = Category.objects.get(type="Transfer_from")
                tx_from.description = f"Transfer to {new_to_acc.name}. {new_description}"
                tx_from.transaction_time = new_time
                tx_from.save(update_fields=["account", "amount", "category", "description", "transaction_time"])

                tx_to.account = new_to_acc
                tx_to.amount = new_amount
                tx_to.category = Category.objects.get(type="Transfer_to")
                tx_to.description = f"Transfer from {new_from_acc.name}. {new_description}"
                tx_to.transaction_time = new_time
                tx_to.save(update_fields=["account", "amount", "category", "description", "transaction_time"])

            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect("all_transactions")

            # return redirect("transfer_list")

    else:
        # Инициализация формы текущими значениями
        form = TransferForm(initial={
            "from_account": tx_from.account,
            "to_account": tx_to.account,
            "amount": tx_from.amount,
            "category": tx_from.category,
            "description": tx_from.description.replace(f"Transfer to {tx_to.account.name}. ", ""),
            "transaction_time": tx_from.transaction_time,
        })

    return render(request, "transaction/edit_transfer.html", {
        "form": form,
        "transfer_id": transfer_id,
    })

@login_required
def delete_transaction(request, pk):
    tx = get_object_or_404(Transaction, pk=pk)

    # Игнорируем переводы — для них отдельная вьюха
    if tx.category and tx.category.type.lower().startswith("transfer"):
        return redirect("transfer_list")

    # Вычисляем эффект на счёт
    if request.method == "POST":
        def effect(amount, typ):
            if typ.lower() == "income":
                return Decimal(amount)
            elif typ.lower() == "outcome":
                return -Decimal(amount)
            else:
                return Decimal(0)

        old_effect = effect(tx.amount, tx.category.type if tx.category else None)

        with db_transaction.atomic():
            tx.account.balance -= old_effect
            tx.account.save(update_fields=["balance"])
            tx.delete()

        next_url = request.POST.get('next')
        if next_url:
            return redirect(next_url)
        else:
            return redirect("all_transactions")

        # # Редирект на соответствующий список
        # if tx.category.type.lower() == "income":
        #     return redirect("income_list")
        # else:
        #     return redirect("outcome_list")


@login_required
def delete_transfer(request, transfer_id):
    """Удаляет обе связанные части перевода и откатывает балансы."""
    tx_from = get_object_or_404(Transaction, transfer_id=transfer_id, category__type="Transfer_from")
    tx_to = get_object_or_404(Transaction, transfer_id=transfer_id, category__type="Transfer_to")

    from_acc = tx_from.account
    to_acc = tx_to.account
    amount = Decimal(tx_from.amount)

    if request.method == "POST":
        with db_transaction.atomic():
            # Откатываем эффект перевода
            from_acc.balance += amount
            from_acc.save(update_fields=["balance"])

            to_acc.balance -= amount
            to_acc.save(update_fields=["balance"])

            # Удаляем обе транзакции
            tx_from.delete()
            tx_to.delete()

        next_url = request.POST.get('next')
        if next_url:
            return redirect(next_url)
        else:
            return redirect("all_transactions")

        # return redirect("transfer_list")
