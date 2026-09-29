from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from .models import SalesOrder
from .serializers import SalesOrderSerializer
from rest_framework.views import APIView
from django.db import transaction
from django.shortcuts import get_object_or_404
from inventory.models import Inventory, StockTransaction
from rest_framework.response import Response


class SalesOrderListCreateView(generics.ListCreateAPIView):
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer
    permission_classes = [IsAuthenticated]
        
class SalesOrderDetailView(generics.RetrieveAPIView):
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer
    permission_classes = [IsAuthenticated]
    
class ConfirmOrderView(APIView):
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request, pk):
        order = get_object_or_404(SalesOrder, pk=pk)
        
        if order.status != 'DRAFT':
            return self.response(
                {
                    'detail': 'Only draft orders can be confirmed'
                }, status=status.HTTP_400_BAD_REQUEST
            )
            
        items = order.items.select_related('product')
        
        for item in items:
            inventory = (Inventory.objects.select_for_update().filter(product=item.product).first())
            
            if inventory is None:
                return Response(
                    {
                        (f"No inventory found for " f"{item.product.name}")                     
                    }, status=status.HTTP_400_BAD_REQUEST
                )
                
                
            if inventory.quantity < item.quantity:
                return Response(
                    {
                        'detail': (f"Insufficient stock for " f"{item.product.name}")
                    }, status=status.HTTP_400_BAD_REQUEST
                )
        
        for item in items:
            inventory = (Inventory.objects.select_for_update().get(product=item.product))
            inventory.save()
            
            StockTransaction.objects.create(product=item.product, transaction_type='OUT', quantity=item.quantity)
            order.status = 'CONFIRMED'
            order.save()
            
            return Response(
                {
                    'detail': ('Order confirmed successfully'),
                    'order_id': order.id,
                    'status': order.status
                }, status=status.HTTP_200_OK
            )