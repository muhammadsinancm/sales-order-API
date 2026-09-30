from django.db import transaction
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from products.models import Product
from .models import Inventory, StockTransaction
from .serializers import (InvontorySerializer, StockTransactionSerializer, StockMovementSerializer)
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema

class InventoryDetailView(generics.RetrieveAPIView):
    queryset = Inventory.objects.select_related('product')
    serializer_class = InvontorySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'product_id'

    # def get_object(self):
    #     product_id = self.kwargs['product_id']
    #     product = Product.objects.get(id=product_id)
    #     inventory, created = Inventory.objects.get_or_create(product=product)
    #     return inventory

class StockTransactionListView(generics.ListAPIView):
    serializer_class = StockTransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return StockTransaction.objects.filter(product_id=product_id).select_related('product').order_by('-created_at')
    
@extend_schema(request=StockMovementSerializer)
class StockInView(generics.CreateAPIView):
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, reqeust, *args, **kwargs):
        serializer = self.get_serializer(data=reqeust.data)
        serializer.is_valid(raise_exception=True)
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        
        try:
            product = Product.objects.get(id=product_id)
        
        except Product.DoesNotExist:
            return Response(
                {
                    'detail' : 'Product not found'
                }, status=status.HTTP_404_NOT_FOUND
            )
        
        # product = get_object_or_404(Product, id=product_id)
        
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

@extend_schema(request=StockMovementSerializer)
class StockOutView(generics.CreateAPIView):
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, reqeust, *args, **kwargs):
        serializer = self.get_serializer(data=reqeust.data)
        serializer.is_valid(raise_exception=True)
        
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        
        try:
            product = Product.objects.get(id=product_id)
        
        except Product.DoesNotExist:
            return Response(
                {
                    'detial' : 'product not found'
                }, status=status.HTTP_404_NOT_FOUND
            )
        
        # product = get_object_or_404(Product, id=product_id)
        
        try:
            inventory = Inventory.objects.select_for_update().get(product=product)
        
        except Inventory.DoesNotExist:
            return Response(
                {
                    'detail' : 'Inventory does not exist' 'for this product'
                }, status=status.HTTP_404_NOT_FOUND
            )
            
        if inventory.quantity < quantity:
            return Response(
                {
                    'detail' : 'Insufficient stock',
                    'current_stock' : inventory.quantity,
                    'requested_queantity' : quantity
                }, status=status.HTTP_400_BAD_REQUEST
            )
        
        inventory.quantity -= quantity
        inventory.save()
        
        StockTransaction.objects.create(product=product, transaction_type='OUT', quantity=quantity)
        
        return Response({
            'message': 'Stock removed successfully',
            'product_id': product.id,
            'quantity_removed': quantity,
            'current_stock': inventory.quantity
            }, status=status.HTTP_200_OK)