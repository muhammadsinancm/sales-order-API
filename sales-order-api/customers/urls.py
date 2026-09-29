from django.urls import path
from .views import CustomerListCreateView, CustomerDetailsView

urlpatterns = [
    path('', CustomerListCreateView.as_view(), name='customer-list-create'),
    path('<int:pk>/', CustomerDetailsView.as_view(), name='customer-detail')
]