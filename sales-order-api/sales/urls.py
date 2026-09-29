from django.urls import path
from .views import SalesOrderListCreateView

urlpatterns = [
    path('', SalesOrderListCreateView.as_view(), name='order-list-create')
]
