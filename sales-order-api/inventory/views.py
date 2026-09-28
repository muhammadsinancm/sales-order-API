from django.db import transaction
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from products.models import Product
from .models import Inventory, StockTransaction
from .serializers import (InvontorySerializer, StockTransactionSerializer, StockMovementSerializer)
from django.shortcuts import get_object_or_404

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
        return StockTransaction.objects.filter(product_id=product_id).order_by('-created_at')
    
class StockInView(APIView):
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, reqeust):
        serializer = StockMovementSerializer(data=reqeust.data)
        serializer.is_valid(raise_exception=True)
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        
        product = get_object_or_404(Product, id=product_id)
        
        inventory, created = Inventory.objects.select_for_update().get_or_create(product=product)
        
        inventory.quantity += quantity
        inventory.save()
        
        StockTransaction.objects.create(product=product, transaction_type='IN', quantity=quantity)
        
        return Response(
            {
                'message': 'Stock added successfully',
                'product_id': product.id,
                'quantity_added': quantity,
                'current_stock': inventory.quantity
            },
            status=status.HTTP_200_OK
        )