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