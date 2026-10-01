from rest_framework import serializers
from .models import Supplier, RequestForQuotation, RFQItem
from django.db import transaction

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'phone', 'email', 'address', 'created_at', 'updated_at'
        ]
        
        read_only_fields = [
            'id', 'created_at', 'updated_at'
        ]

class REQItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RFQItem
        fields = [
            'id', 'product', 'quantity', 'notes'
        ]
        
        read_only_fields = [
            'id', 'created_at', 'updated_at'
        ]
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError( "Quantity must be greater than 0.")
        return value
    
class RequestForQuotationSerializer(serializers.ModelSerializer):
    items = REQItemSerializer(many=True)
    class Meta:
        model = RequestForQuotation
        fields = [
            'id', 'supplier', 'status', 'quotation_date', 'notes', 'items', 'created_at', 'updated_at'
        ]
        
        read_only_fields = [
            'id', 'created_at', 'updated_at'
        ]
        
    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        rfq = RequestForQuotation.objects.create(**validated_data)
        
        for item_data in items_data:
            RFQItem.objects.create(rfq=rfq, **item_data)
        return rfq