from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from .models import SalesOrder, SalesOrderItem

class SalesOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrderItem
        fields = [
            'id', 'product', 'quantity', 'unit_price', 'tax_rate', 'subtotal', 'tax', 'total'
        ]
        
        read_only_fields = [
            'id', 'unit_price', 'tax_rate', 'subtotal', 'tax', 'total'
        ]
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError('Quantity must be greater than 0')
        return value
        
class SalesOrderSerializer(serializers.ModelSerializer):
    items = SalesOrderItemSerializer(many=True)
    
    class Meta:
         model = SalesOrder
         fields = [
             'id', 'customer', 'status', 'items', 'discount', 'subtotal', 'tax', 'grand_total', 'created_at', 'updated_at'
         ]
         
         read_only_fields = [
             'id', 'status', 'subtotal', 'tax', 'grand_total', 'created_at', 'updated_at'
         ]
    
    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        discount = validated_data.get('discount', Decimal('0'))
        order = SalesOrder.objects.create(**validated_data)
        subtotal = Decimal('0')
        total_tax = Decimal('0')
        
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            
            unit_price = product.price
            tax_rate = product.tax_rate
            
            item_subtotal = unit_price * quantity
            
            item_tax = (item_subtotal * tax_rate / Decimal('100'))
            
            item_total = item_subtotal + item_tax
            
            SalesOrderItem.objects.create(order=order, product=product, quantity=quantity, unit_price=unit_price, tax_rate=tax_rate, subtotal=item_subtotal, tax=item_tax, total=item_total)
            
            subtotal += item_subtotal
            total_tax += item_tax
            
        order.subtotal = subtotal
        order.tax = total_tax
        order.grand_total = (subtotal - discount + total_tax)
        order.save()
        
        return order