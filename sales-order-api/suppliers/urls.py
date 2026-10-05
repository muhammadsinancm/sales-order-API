from django.urls import path
from .views import SupplierListCreateView, SupplierDetailView, RFQListCreateView, RFQDetailView, SupplierQuotationListCreateView, SupplierQuotationDetailView, SupplierQuotationSendView

urlpatterns = [
    path('rfqs/', RFQListCreateView.as_view(), name='rfq-list-create'),
    path('rfqs/<int:pk>/', RFQDetailView.as_view(), name='rfq-detail'),
    path('quotations/', SupplierQuotationListCreateView.as_view(), name='quotation-List-create'),
    path('quotations/<int:pk>/', SupplierQuotationDetailView.as_view(), name='quotation-detail'),
    path('quotations/<int:pk>/send/', SupplierQuotationSendView.as_view(), name='quotation-send'),
    path('', SupplierListCreateView.as_view(), name='supplier-list-create'),
    path('<int:pk>/', SupplierDetailView.as_view(), name='supplier-detail')
]