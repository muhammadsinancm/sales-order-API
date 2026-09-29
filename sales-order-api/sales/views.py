from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from .models import SalesOrder
from .serializers import SalesOrderSerializer
from rest_framework.views import APIView
from django.db import transaction
from django.shortcuts import get_object_or_404

class SalesOrderListCreateView(generics.ListCreateAPIView):
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer
    permission_classes = [IsAuthenticated]
        
class SalesOrderDetailView(generics.RetrieveAPIView):
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer
    permission_classes = [IsAuthenticated]
    
# class ConfirmOrderView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     @transaction.atomic
#     def post(self, request, pk):
#         order = get_object_or_404(SalesOrder, pk=pk)
        
#         if order.status != 'DRAFT':
#             return self.response(
#                 {
#                     'detail': 'Only draft orders can be confirmed'
#                 }, status=status.HTTP_400_BAD_REQUEST
#             )
            
            
#         for item in order.items.select_related('product'):
#             inventory = Inventory.object.select_for_update().filter(product=item.prudct).first()