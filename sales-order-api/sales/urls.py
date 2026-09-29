from django.urls import path
from .views import (SalesOrderListCreateView, SalesOrderDetailView, ConfirmOrderView, ProcessOrderView, CompleteOrderView)

urlpatterns = [
    path('', SalesOrderListCreateView.as_view(), name='order-list-create'),
    path('<int:pk>/', SalesOrderDetailView.as_view(), name='order-detail'),
    path('<int:pk>/confirm/', ConfirmOrderView.as_view(), name='order-confirm'),
    path('<int:pk>/processing/', ProcessOrderView.as_view(), name='order-processing'),
    path('<int:pk>/complete/', CompleteOrderView.as_view(), name='order-complete')
]
