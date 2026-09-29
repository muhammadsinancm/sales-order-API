from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from .models import SalesOrder
from .serializers import SalesOrderSerializer
from rest_framework.views import APIView
from django.db import transaction
from django.shortcuts import get_object_or_404
from inventory.models import Inventory, StockTransaction
from rest_framework.response import Response
from audit.models import AuditLog
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

class SalesOrderListCreateView(generics.ListCreateAPIView):
    queryset = SalesOrder.objects.all().order_by('-created_at')
    serializer_class = SalesOrderSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [
        DjangoFilterBackend, OrderingFilter
    ]
    
    filterset_fields = [
        'status', 'customer'
    ]
    
    ordering_fields = [
        'created_at', 'grand_total', 'status'
    ]
    
    ordering = ['-created_at']
        
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
            
            AuditLog.objects.create(user=request.user, action='ORDER_CONFIRMED', entity_type='SalesOrder', entity_id=order.id, details={'status': order.status})
            
            return Response(
                {
                    'detail': ('Order confirmed successfully'),
                    'order_id': order.id,
                    'status': order.status
                }, status=status.HTTP_200_OK
            )
            
class ProcessOrderView(APIView):
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request, pk):
        order = get_object_or_404(SalesOrder, id=pk)
        
        if order.status != 'CONFIRMED':
            return Response(
                {
                    'detail': 'Only confirmed orders can be moved to processing'
                }, status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'PROCESSING'
        order.save()
        AuditLog.objects.create(user=request.user, action='ORDER_PROCESSING', entity_type='SalesOrder', entity_id=order.id, details={'status': order.status})
        
        return Response(
            {
                'message' : 'Order moved to processing successfully',
                'order_id': order.id,
                'status': order.status
            }, status=status.HTTP_200_OK
        )
        
class CompleteOrderView(APIView):
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request, pk):
        order = get_object_or_404(SalesOrder, pk=pk)
        
        if order.status != 'PROCESSING':
            return Response(
                {
                    'detail' : 'Only processing orders can be completed'
                }, status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'COMPLETED'
        order.save()
        
        AuditLog.objects.create(
            user=request.user, action='ORDER_COMPLETED', entity_type='SalesOrder', entity_id=order.id, details={'status' : order.status}
        )
        
        return Response(
            {
                'message': 'Order completed successfully',
                'order_id' : order.id,
                'status' : order.status
            }, status=status.HTTP_200_OK
        )
    
class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request, pk):
        order = get_object_or_404(SalesOrder, pk=pk)
        
        if order.status in ['COMPLETED', 'CANCELLED']:
            return Response(
                {
                    'detail' : 'This order can not be cancelled'
                }, status=status.HTTP_400_BAD_REQUEST
            )
            
        if order.status in ['CONFIRMED', 'PROCESSING']:
            items = order.items.select_related('product')
            
            for item in items:
              inventory = (Inventory.objects.select_for_update().filter(product=item.product).first())
              
              if inventory is None:
                  return Response(
                      {
                          'detail': f"No inventory found for {item.product.name}"
                      }, status=status.HTTP_400_BAD_REQUEST
                  )
                
            inventory.quantity += item.quantity
            inventory.save()
            
            StockTransaction.objects.create(product=item.product, transaction_type='IN', quantity=item.quantity)
        
        order.status = 'CANCELLED'
        order.save()
        
        AuditLog.objects.create(
            user=request.user, action='ORDER_CANCELLED', entity_type='SalesOrder', entity_id=order.id, detail={'status' : order.status}
        )
        
        return Response(
            {
                'message' : 'Order cancelled successfully',
                'order_id' : order.id,
                'status' : order.status
            }, status=status.HTTP_200_OK
        )
            