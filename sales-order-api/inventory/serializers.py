from rest_framework import serializers
from .models import Inventory, StockTransaction
from products.serializers import ProductSerializer

class InvontorySerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = Inventory
        fields = [
            'id', 'product', 'quantity', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'product', 'quantity', 'created_at', 'updated_at'
        ]

class StockTransactionSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = StockTransaction
        fields = [
            'id', 'product', 'transaction_type', 'quantity', 'created_at'
        ]
        read_only_fields = [
            'id', 'product', 'transaction_type', 'quantity', 'created_at'
        ]
    
class StockMovementSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)