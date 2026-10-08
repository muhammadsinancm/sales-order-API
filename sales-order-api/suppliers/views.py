from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import PurchaseOrder, Supplier, RequestForQuotation, SupplierQuotation, GoodsReceipt
from .serializers import SupplierQuotationSerializer, SupplierSerializer, RequestForQuotationSerializer, PurchaseOrderSerializer, GoodsReceiptSerializer
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status

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
        quotation.req.status = 'RECEIVED'
        quotation.rfq.save()
        
        return Response(
            {
                "message": ("Quotation accepted successfully."),
                "status": 'ACCEPTED',
            },
            status=status.HTTP_200_OK
        )
    
class SupplierQuotationRejectView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
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
        
class SupplierQuotationCancelView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
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
    
class PurchaseOrderApproveView(generics.UpdateAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        order =self.get_object()
        
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
            }
        )
        
class PurchaseOrderSendView(generics.UpdateAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        order = self.get_object()

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
            }
        )
        
class PurchaseOrderCancelView(generics.UpdateAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        order = self.get_object()

        if order.status in [
            "RECEIVED",
            "CANCELLED",
        ]:

            return Response(
                {
                    "detail": ("Purchase order cannot " "be cancelled.")
                }, status=status.HTTP_400_BAD_REQUEST
            )

        order.status = "CANCELLED"
        order.save()
        
        return Response(
            {
                "message": ("Purchase order cancelled."),
                "status": order.status,
            }
        )
        
class GoodsReceiptListCreateView(generics.ListCreateAPIView):
    queryset = (GoodsReceipt.objects.select_related("purchase_order").prefetch_related("items__purchase_order_item__product"))
    serializer_class = GoodsReceiptSerializer
    permission_classes = [IsAuthenticated]
    
class GoodsReceiptDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = (GoodsReceipt.objects.select_related("purchase_order").prefetch_related("items__purchase_order_item__product"))
    serializer_class = GoodsReceiptSerializer
    permission_classes = [IsAuthenticated]