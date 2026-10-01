from django.urls import path
from .views import SupplierListCreateView, SupplierDetailView, RFQListCreateView, REQDetailView

urlpatterns = [
    path('', SupplierListCreateView.as_view(), name='supplier-list-create'),
    path('<int:pk>/', SupplierDetailView.as_view(), name='supplier-detail'),
    path('rfqs/', RFQListCreateView.as_view(), name='rfq-list-create'),
    path('rfqs/<int:pk>/', REQDetailView.as_view(), name='rfq-detail')
]
