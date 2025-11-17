from django import forms
from django.utils import timezone
from .models import Account, Category, Transaction


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['name', 'iban', 'currency', 'balance']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'iban': forms.TextInput(attrs={'class': 'form-control'}),
            'balance': forms.NumberInput(attrs={'class': 'form-control'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'type', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
        }


class TransactionForm(forms.ModelForm):
    transaction_time = forms.DateTimeField(
        label="Transaction time",
        initial=timezone.now,
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
                "class": "form-control"
            }
        ),
        input_formats=[
            "%Y-%m-%dT%H:%M",  # 👈 формат iPhone Safari
            "%Y-%m-%d %H:%M:%S",  # стандарт Django
            "%Y-%m-%d %H:%M",  # fallback
        ]
    )

    class Meta:
        model = Transaction
        fields = ["amount", "account", "category", "transaction_time", "description"]

    def __init__(self, *args, **kwargs):
        tx_type = kwargs.pop("tx_type", None)
        super().__init__(*args, **kwargs)

        if tx_type:
            self.fields["category"].queryset = Category.objects.filter(type=tx_type)

        for field in ["amount", "account", "category", "description"]:
            self.fields[field].widget.attrs.update({"class": "form-control"})

        # Для поля amount — особая настройка, чтобы не показывало 0 на iPhone
        self.fields["amount"].widget = forms.NumberInput(
            attrs={
                "class": "form-control",
                "inputmode": "decimal",  # помогает iPhone не подставлять 0
                "value": "",             # явно указываем пустое значение
                "step": "any",
                "placeholder": "",
            }
        )

class TransferForm(forms.Form):
    from_account = forms.ModelChoiceField(
        queryset=Account.objects.all(),
        label="From account",
        widget=forms.Select(attrs={"class": "form-control"})
    )
    to_account = forms.ModelChoiceField(
        queryset=Account.objects.all(),
        label="To account",
        widget=forms.Select(attrs={"class": "form-control"})
    )
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "inputmode": "decimal",  # чтобы на iPhone не появлялся 0
                "value": "",             # пустое поле по умолчанию
                "step": "any",
                "placeholder": "",
            }
        )
    )
    # # category = forms.ModelChoiceField(
    # #     queryset=Category.objects.filter(type="Transfer_from"),
    # #     label="Category",
    # #     widget=forms.Select(attrs={"class": "form-control"})
    # )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3})
    )

    transaction_time = forms.DateTimeField(
        label="Transaction time",
        initial=timezone.now,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"})
    )

    def clean(self):
        cleaned_data = super().clean()
        from_acc = cleaned_data.get("from_account")
        to_acc = cleaned_data.get("to_account")

        if from_acc == to_acc:
            raise forms.ValidationError("Source and destination accounts cannot be the same.")
        return cleaned_data
