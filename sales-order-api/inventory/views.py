from django.db import transaction
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from products.models import Product
from .models import Inventory, StockTransaction
from .serializers import InvontorySerializer, StockTransactionSerializer

class InventoryDetailView(generics.RetrieveAPIView):
    serializer_class = InvontorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        product_id = self.kwargs['product_id']
        product = Product.objects.get(id=product_id)
        inventory, created = Inventory.objects.get_or_create(product=product)
        return inventory

class StockTransactionListView(generics.ListAPIView):
    serializer_class = StockTransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return StockTransaction.objects.filter(product_id=product_id).order_by('-created_aty')