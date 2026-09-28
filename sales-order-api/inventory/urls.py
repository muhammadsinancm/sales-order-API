from django.urls import path
from .views import (InventoryDetailView, StockTransactionListView)

urlpatterns = [
    path('<int:product_id>/', InventoryDetailView.as_view(), name='Inventory-detail'),
    path('<int:product_id>/transactions/', StockTransactionListView.as_view(), name='stock-transaction-list')
]
