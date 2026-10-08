from django.urls import path
from .views import ( PurchaseOrderApproveView, PurchaseOrderCancelView, PurchaseOrderDetailView, PurchaseOrderListCreateView, PurchaseOrderSendView, SupplierListCreateView, SupplierDetailView, RFQListCreateView, RFQDetailView, RFQSendView, RFQCancelView, SupplierQuotationListCreateView, SupplierQuotationDetailView, SupplierQuotationSendView, SupplierQuotationAcceptView, SupplierQuotationRejectView, SupplierQuotationCancelView, GoodsReceiptListCreateView, GoodsReceiptDetailView, GoodsReceiptReceiveView)

urlpatterns = [
    path('', SupplierListCreateView.as_view(), name='supplier-list-create'),
    path('<int:pk>/', SupplierDetailView.as_view(), name='supplier-detail'),
    path('rfqs/', RFQListCreateView.as_view(), name='rfq-list-create'),
    path('rfqs/<int:pk>/', RFQDetailView.as_view(), name='rfq-detail'),
    path('rfqs/<int:pk>/send/', RFQSendView.as_view(), name='rfq-send'),
    path("rfqs/<int:pk>/cancel/", RFQCancelView.as_view(), name="rfq-cancel"),
    path('quotations/', SupplierQuotationListCreateView.as_view(), name='quotation-List-create'),
    path('quotations/<int:pk>/', SupplierQuotationDetailView.as_view(), name='quotation-detail'),
    path('quotations/<int:pk>/send/', SupplierQuotationSendView.as_view(), name='quotation-send'),
    path('quotations/<int:pk>/accept/', SupplierQuotationAcceptView.as_view(), name='quotation-accept'),
    path("quotations/<int:pk>/reject/", SupplierQuotationRejectView.as_view(), name="quotation-reject"),
    path("quotations/<int:pk>/cancel/", SupplierQuotationCancelView.as_view(), name="quotation-cancel"),
    path("purchase-orders/", PurchaseOrderListCreateView.as_view(), name="purchase-order-list-create"),
    path("purchase-orders/<int:pk>/", PurchaseOrderDetailView.as_view(), name="purchase-order-detail"),
    path("purchase-orders/<int:pk>/approve/", PurchaseOrderApproveView.as_view(), name="purchase-order-approve"),
    path("purchase-orders/<int:pk>/send/", PurchaseOrderSendView.as_view(), name="purchase-order-send"),
    path("purchase-orders/<int:pk>/cancel/", PurchaseOrderCancelView.as_view(), name="parchase-order-cancel"),
    path("goods-receipts/", GoodsReceiptListCreateView.as_view(), name="goods-receipt-liset-create"),
    path("goods-receipts/<int:pk>/", GoodsReceiptDetailView.as_view(), name="goods-receipt-detail"),
    path('goods-receipts/<int:pk>/receive/', GoodsReceiptReceiveView.as_view(), name='goods-receipt-receive')
]