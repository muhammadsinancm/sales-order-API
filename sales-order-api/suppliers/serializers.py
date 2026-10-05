from rest_framework import serializers
from .models import Supplier, RequestForQuotation, RFQItem, SupplierQuotationItem, SupplierQuotation
from django.db import transaction
from decimal import Decimal

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'phone', 'email', 'address', 'created_at', 'updated_at'
        ]
        
        read_only_fields = [
            'id', 'created_at', 'updated_at'
        ]

class RFQItemSerializer(serializers.ModelSerializer):
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
    items = RFQItemSerializer(many=True)
    class Meta:
        model = RequestForQuotation
        fields = [
            'id', 'supplier', 'status', 'quotation_date', 'notes', 'items', 'created_at', 'updated_at'
        ]
        
        read_only_fields = [
            'id', 'status', 'created_at', 'updated_at'
        ]
        
    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        rfq = RequestForQuotation.objects.create(**validated_data)
        
        for item_data in items_data:
            RFQItem.objects.create(rfq=rfq, **item_data)
        return rfq
    
    @transaction.atomic
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        
        instance.supplier = validated_data.get('supplier', instance.supplier)
        instance.status = validated_data.get('status', instance.status)
        instance.quotation_date = validated_data.get('quotation_date', instance.quotation_date)
        instance.notes = validated_data.get('notes', instance.notes)
        instance.save()
        
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                RFQItem.objects.create(rfq=instance, **item_data)
        
        return instance
    
class SupplierQuotationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierQuotationItem
        fields = [
            'id', 'product', 'quantity', 'unit_price', 'tax_rate', 'subtotal', 'tax', 'total'
        ]
        
        read_only_fields = [
            'id', 'subtotal', 'tax', 'total'
        ]
        
        def validate_quantity(self, value):
            if value <= 0:
                raise serializers.ValidationError('Quantity must be greater than 0.')
            return value
        
        def validate_unit_price(self, value):
            if value < 0:
                raise serializers.ValidationError('Unit price can not be negative.')
            return value
        
        def validate_tax_rate(self, value):
            if value < 0:
                raise serializers.ValidationError('Tax rate can not be negative.')
            return value
        
class SupplierQuotationSerializer(serializers.ModelSerializer):
    items = SupplierQuotationItemSerializer(many=True)
    
    class Meta:
        model = SupplierQuotation
        fields = [
            'id', 'rfq', 'supplier', 'status', 'quotation_number', 'quotation_date', 'valid_until', 'notes', 'items', 'subtotal', 'tax', 'grand_total', 'created_at', 'updated_at'
        ]
        
        read_only_fields = [
            'id', 'status', 'subtotal', 'tax', 'grand_total', 'created_at', 'updated_at'
        ]
        
        @transaction.atomic
        def create(self, validate_data):
            items_data = validate_data.pop('items')
            
            quotation = SupplierQuotation.objects.create(**validate_data)
            
            for item_data in items_data:
                SupplierQuotationItem.objects.create(quotation=quotation, **item_data)
                
            subtotal = sum((item.subtotal for item in quotation.items.all()), Decimal('0'))
            tax = sum((item.tax for item in quotation.items.all()), Decimal('0'))
            
            quotation.subtotal = subtotal
            quotation.tax = tax
            quotation.grand_total = subtotal + tax
            quotation.save()

            return quotation
        
        @transaction.atomic
        def update(self, instance, validated_data):
            items_data = validated_data.pop('items', None)
            
            if items_data is not None:
                instance.items.all().delete()
                for item_data in items_data:
                    SupplierQuotationItem.objects.create(quotation=instance, **item_data)
                    
            instance.supplier = validated_data.get('supplier', instance.supplier)
            instance.rfq = validated_data.get('rfq', instance.rfq)
            instance.quotation_number = validated_data.get('quotation_number', instance.quotation_number)
            instance.quotation_date = validated_data.get('quotation_date', instance.quotation_date)
            instance.valid_until = validated_data.get('valid_until', instance.valid_until)
            instance.notes = validated_data.get('notes', instance.notes)
            instance.save()
            
            subtotal = sum((item.subtotal for item in instance.items.all()), Decimal('0'))
            tax = ((item.tax for item in instance.items.all()), Decimal('0'))
            
            instance.subtotal = subtotal
            instance.tax = tax
            instance.grand_total = subtotal + tax
            
            instance.save()
            
            return instance