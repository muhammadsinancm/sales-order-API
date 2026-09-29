from django.urls import path
from .views import SalesOrderListCreateView, SalesOrderDetailView

urlpatterns = [
    path('', SalesOrderListCreateView.as_view(), name='order-list-create'),
    path('<int:pk>/', SalesOrderDetailView.as_view(), name='order-detail')
]
