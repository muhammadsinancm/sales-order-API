from django.urls import path
from .views import (InventoryDetailView, StockTransactionListView, StockInView, StockOutView)

urlpatterns = [
    path('stock-in/', StockInView.as_view(), name='stock-in'),
    path('stock-out/', StockOutView.as_view(), name='stock-out'),
    path('<int:product_id>/transactions/', StockTransactionListView.as_view(), name='stock-transaction-list'),
    path('<int:product_id>/', InventoryDetailView.as_view(), name='Inventory-detail'),
]
