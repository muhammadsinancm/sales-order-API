from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from .models import Supplier, RequestForQuotation, SupplierQuotation
from .serializers import SupplierQuotationSerializer, SupplierSerializer, RequestForQuotationSerializer
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
    queryset = RequestForQuotation.objects.prefetch_related('items').select_related('supplier')
    serializer_class = RequestForQuotationSerializer
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save()
        
class RFQDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RequestForQuotation.objects.prefetch_related('items').select_related('supplier')
    serializer_class = RequestForQuotationSerializer
    permission_classes = [IsAuthenticated]
    
class SupplierQuotationListCreateView(generics.ListCreateAPIView):
    queryset = SupplierQuotation.objects.select_related('rfq', 'supplier').prefetch_related('items')
    serializer_class = SupplierQuotationSerializer
    permission_classes = [IsAuthenticated]
    
class SupplierQuotationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SupplierQuotation.objects.select_related('rfq', 'supplier').select_related('items')
    serializer_class = SupplierQuotationSerializer
    permission_classes = [IsAuthenticated]
    
class SupplierQuotationSendView(generics.GenericAPIView):
    queryset = SupplierQuotation.objects.all()
    serializer_class = SupplierQuotationSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        quotation = self.get_object()
        
        if quotation.status != 'DRAFT':
            return Response(
                {
                    'detail' : 'Only a DRAFT quotation can be sent.' 
                }, status=status.HTTP_400_BAD_REQUEST
            )
            
        quotation.status = 'SENT'
        quotation.save(update_fields=['status', 'updated_at'])
        
        serializer = self.get_serializer(quotation)
        
        return Response(serializer.data, status=status.HTTP_200_OK)