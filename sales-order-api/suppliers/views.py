from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Supplier, RequestForQuotation
from .serializers import SupplierSerializer, RequestForQuotationSerializer
from django.db import transaction

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
        
class REQDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RequestForQuotation.objects.prefetch_related('items').select_related('supplier')
    serializer_class = RequestForQuotationSerializer
    permission_classes = [IsAuthenticated]