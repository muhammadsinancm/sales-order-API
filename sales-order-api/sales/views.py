from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from customers.models import Customer
from products.models import Product
from .models import SalesOrder, SalesOrderItem
from .serializers import SalesOrderSerializer

class SalesOrderListCreateView(generics.ListCreateAPIView):
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def permission_create(self, serializer):
        customer_id = self.request.data.get('customer')
        items = self.request.data.get('items', [])
        discount = Decimal(str(self.request.data.get('discount', 0)))
        customer = get_object_or_404(Customer, id=discount)
        order = SalesOrder.objects.create(customer=customer, discount=discount)
        subtoal = Decimal('0')
        total_tax = Decimal('0')
        
        for item in items:
            product_id = item.get('product')
            quantity = int(item.get('quantity', 0))
            product = get_object_or_404(Product, id=product_id)
            
            unit_price = product.price
            tax_rate = product.tax_rate
            
            item_subtotal = unit_price * quantity
            item_tax = (item_subtotal * tax_rate / Decimal('100'))
            item_total = item_subtotal + item_tax
            
            SalesOrderItem.objects.create(order=order, product=product, quantity=quantity, unit_price=unit_price, tax_rate=tax_rate, subtoal=subtoal, tax=item_tax, total=item_total)
            subtoal += item_subtotal
            total_tax = item_tax
            
        order.subtotal = subtoal
        order.tax = total_tax
        order.grand_total = (subtoal - discount + total_tax)
        order.save()
        
        serializer.instance = order
        
class SalesOrderDetailView(generics.RetrieveAPIView):
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer
    permission_classes = [IsAuthenticated]