from django.urls import path
from . import views

urlpatterns = [
    path('account/create/', views.create_account, name='create_account'),
    path('bank_cash/', views.bank_and_cash, name='bank_and_cash'),
    path('account/<int:account_id>/', views.account_detail, name='account_detail'),
    path('account/<int:account_id>/delete/', views.account_delete, name='account_delete'),
    path('category/create/', views.create_category, name='create_category'),
    path('category/', views.category, name='category'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('category/<int:category_id>/delete/', views.category_delete, name='category_delete'),
    path("income/", views.income_list, name="income_list"),
    path("outcome/", views.outcome_list, name="outcome_list"),
    path("transfer/", views.transfer_list, name="transfer_list"),
    path("add/transfer/", views.add_transfer, name="add_transfer"),
    path("add/<str:tx_type>/", views.add_transaction, name="add_transaction"),
    path("transaction/<int:pk>/edit/", views.edit_transaction, name="edit_transaction"),
    path("transaction/<uuid:transfer_id>/edit_transfer/", views.edit_transfer, name="edit_transfer"),
    path("transaction/<int:pk>/delete/", views.delete_transaction, name="delete_transaction"),
    path("transaction/<uuid:transfer_id>/delete_transfer/", views.delete_transfer, name="delete_transfer"),
    path("transactions/all/", views.all_transactions, name="all_transactions"),
]
