from itertools import product
from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import PurchaseOrder, Supplier, RequestForQuotation, SupplierQuotation, GoodsReceipt
from .serializers import SupplierQuotationSerializer, SupplierSerializer, RequestForQuotationSerializer, PurchaseOrderSerializer, GoodsReceiptSerializer
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from inventory.models import Inventory, StockTransaction

class SupplierListCreateView(generics.ListCreateAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    
class SupplierDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer     
    permission_classes = [IsAuthenticated]
    
class RFQListCreateView(generics.ListCreateAPIView):
    queryset = RequestForQuotation.objects.select_related('supplier').prefetch_related('items__product')
    serializer_class = RequestForQuotationSerializer
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save()
        
class RFQDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RequestForQuotation.objects.select_related('supplier').prefetch_related('items__product')
    serializer_class = RequestForQuotationSerializer
    permission_classes = [IsAuthenticated]
    

class RFQSendView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        rfq = generics.get_object_or_404(RequestForQuotation, pk=kwargs['pk'])
        
        if rfq.status != "DRAFT":
            return Response(
                {
                    "detail": "Only draft RFQs can be sent."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        rfq.status = "SENT"
        rfq.save()

        return Response(
            {
                "message": "RFQ sent successfully.",
                "status": rfq.status,
            },
            status=status.HTTP_200_OK
        )
        
class RFQCancelView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        rfq = generics.get_object_or_404(RequestForQuotation, pk=kwargs['pk'])

        if rfq.status in ["RECEIVED", "CANCELLED"]:
            return Response(
                {
                    "detail": "RFQ cannot be cancelled in its current status."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        rfq.status = "CANCELLED"
        rfq.save()

        return Response(
            {
                "message": "RFQ cancelled.",
                "status": rfq.status,
            },
            status=status.HTTP_200_OK
        )
    
class SupplierQuotationListCreateView(generics.ListCreateAPIView):
    queryset = SupplierQuotation.objects.select_related('rfq', 'supplier').prefetch_related('items__product')
    serializer_class = SupplierQuotationSerializer
    permission_classes = [IsAuthenticated]
    
class SupplierQuotationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SupplierQuotation.objects.select_related('rfq', 'supplier').prefetch_related('items__product')
    serializer_class = SupplierQuotationSerializer
    permission_classes = [IsAuthenticated]
    
class SupplierQuotationSendView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        quotation = SupplierQuotation.objects.get(pk=kwargs['pk'])
        
        if quotation.status != 'DRAFT':
            return Response(
                {
                    'detail' : 'Only a DRAFT quotation can be sent.' 
                }, status=status.HTTP_400_BAD_REQUEST
            )
            
        quotation.status = 'SENT'
        quotation.save()
        
        return Response(
            {
                "message": ("Quotation sent successfully."),
                "status": quotation.status,
            }
        )

class SupplierQuotationAcceptView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        quotation = SupplierQuotation.objects.get(pk=kwargs['pk'])
        
        if quotation.status != 'SENT':
            return Response(
                {
                    'detail' : 'Only a SENT quotation can be accepted.'
                }, status=status.HTTP_400_BAD_REQUEST
            )
            
        quotation.status = 'ACCEPTED'
        quotation.save()
        quotation.rfq.status = 'RECEIVED'
        quotation.rfq.save()
        
        return Response(
            {
                "message": ("Quotation accepted successfully."),
                "status": 'ACCEPTED',
            },
            status=status.HTTP_200_OK
        )
    
class SupplierQuotationRejectView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        quotation = SupplierQuotation.objects.get(pk=kwargs['pk'])
        
        if quotation.status != 'SENT':
            return Response(
                {
                    'detail' : 'Only a SENT quotation can be rejected.'
                }, status=status.HTTP_400_BAD_REQUEST
            )
        
        quotation.status = 'REJECTED'
        quotation.save()
        
        return Response(
            {
                "message": ("Quotation rejected."),
                "status": quotation.status,
            },
            status=status.HTTP_200_OK
        )
        
class SupplierQuotationCancelView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        quotation = SupplierQuotation.objects.get(pk=kwargs['pk'])
        
        if quotation.status in [ "ACCEPTED",
            "CANCELLED"]:
            
            return Response(
                {
                    "detail": (
                        "Quotation cannot be "
                        "cancelled in its current status."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
        quotation.status = 'CANCELLED'
        quotation.save()
        
        return Response(
            {
                "message": "Quotation cancelled.",
                "status": quotation.status,
            },
            status=status.HTTP_200_OK
        )
        
class PurchaseOrderListCreateView(generics.ListCreateAPIView):
    queryset = (PurchaseOrder.objects.select_related('quotation', 'supplier')).prefetch_related('items__product')
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]
    
class PurchaseOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = (PurchaseOrder.objects.select_related('quotation', 'supplier')).prefetch_related('items__product')
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]
    
class PurchaseOrderApproveView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        order = PurchaseOrder.objects.get(pk=kwargs['pk'])
        
        if order.status != 'DRAFT':
            return Response(
                {
                    "detail": (
                        "Only draft purchase orders " "can be approved.")
                },status=status.HTTP_400_BAD_REQUEST
            )

        order.status = "APPROVED"
        order.save()
        
        return Response(
            {
                "message": ("Purchase order approved."),
                "status": order.status,
            },
            status=status.HTTP_200_OK
        )
        
class PurchaseOrderSendView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        order = PurchaseOrder.objects.get(pk=kwargs['pk'])

        if order.status != "APPROVED":

            return Response(
                {
                    "detail": ("Only approved purchase orders " "can be sent.")
                },status=status.HTTP_400_BAD_REQUEST
            )

        order.status = "SENT"
        order.save()

        return Response(
            {
                "message": ("Purchase order sent."),
                "status": order.status,
            },
            status=status.HTTP_200_OK
        )
        
class PurchaseOrderCancelView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        order = PurchaseOrder.objects.get(pk=kwargs['pk'])

        if order.status in [
            "RECEIVED",
            "CANCELLED",
        ]:

            return Response(
                {
                    "detail": ("Purchase order cannot " "be cancelled."),
                }, status=status.HTTP_400_BAD_REQUEST
            )

        order.status = "CANCELLED"
        order.save()
        
        return Response(
            {
                "message": ("Purchase order cancelled."),
                "status": order.status,
            },
            status=status.HTTP_200_OK
        )
        
class GoodsReceiptListCreateView(generics.ListCreateAPIView):
    queryset = (GoodsReceipt.objects.select_related("purchase_order").prefetch_related("items__purchase_order_item__product"))
    serializer_class = GoodsReceiptSerializer
    permission_classes = [IsAuthenticated]
    
class GoodsReceiptDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = (GoodsReceipt.objects.select_related("purchase_order").prefetch_related("items__purchase_order_item__product"))
    serializer_class = GoodsReceiptSerializer
    permission_classes = [IsAuthenticated]
    
class GoodsReceiptReceiveView(generics.GenericAPIView):
    queryset = (GoodsReceipt.objects.select_related("purchase_order").prefetch_related("items__purchase_order_item__product"))
    serializer_class = GoodsReceiptSerializer
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        receipt = (GoodsReceipt.objects.select_for_update().select_related('purchase_order').prefetch_related('items__purchase_order_item__product').get(pk=kwargs['pk']))
        
        if receipt.status != 'DRAFT':
             return Response(
                {
                    "detail": (
                        "Only draft goods receipts "
                        "can be received."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )
             
        purchase_order = receipt.purchase_order
        
        if purchase_order.status not in ['APPROVED', 'SENT', 'PARTIALLY_RECEIVED']:
            return Response(
                {
                    "detail": (
                        "Purchase order cannot receive "
                        "goods in its current status."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        for receipt_item in receipt.items.all():
            po_item = (purchase_order.items.select_for_update().get(id=receipt_item.purchase_order_item_id))
            received_quantity = (receipt_item.received_quantity)
            remaining_quantity = (po_item.quantity - po_item.received_quantity)
            
            if received_quantity > remaining_quantity:
                 return Response(
                    {
                        "detail": (
                            f"Cannot receive "
                            f"{received_quantity} units "
                            f"of {po_item.product.name}. "
                            f"Only {remaining_quantity} "
                            f"units remaining."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            po_item.received_quantity += (received_quantity)
            po_item.save(update_fields=['received_quantity'])
            
            inventory, created = (inventory.objects.select_for.update().fet_or_create(product=po_item.product, default={'quantity': 0}))
            inventory.quantity += received_quantity
            inventory.save()
            
            StockTransaction.objects.create(product=po_item.product, transaction_type='IN', quantity=received_quantity)
        
        receipt.status = 'RECEIVED'
        receipt.save(update_fields=['status', 'updated_at'])
        
        po_item = purchase_order.items.all()
        
        all_received = all(item.received_quantity >= item.quantity for item in po_item)
        
        any_received = any(item.received_quantity > 0 for item in po_item)
        
        if all_received:
            purchase_order.status = 'RECEIVED'
        
        elif any_received:
            purchase_order.status = 'PARTIALLY_RECEIVED'
            
        purchase_order.save(update_fields=['status', 'updated_at'])
        
        return Response(
            {
                "message": "Goods received successfully.",
                "receipt_id": receipt.id,
                "receipt_status": receipt.status,
                "purchase_order_id": purchase_order.id,
                "purchase_order_status": purchase_order.status,
            },
            status=status.HTTP_200_OK
        )