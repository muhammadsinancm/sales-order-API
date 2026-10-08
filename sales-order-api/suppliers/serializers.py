from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import GoodsReceiptItem, GoodsReceipt, PurchaseOrder, PurchaseOrderItem, Supplier, RequestForQuotation, RFQItem, SupplierQuotationItem, SupplierQuotation
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
        
        read_only_fields = ['id',]
    
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
        
    def validate(self, attrs):
        rfq = attrs.get('rfq')
        supplier = attrs.get('supplier')
        
        if rfq and supplier:
            if rfq.supplier_id != supplier.id:
                raise serializers.ValidationError({'supplier' : ('Supplier must the RFQ supplier')})
        return attrs
        
    @transaction.atomic
    def create(self, validate_data):
        items_data = validate_data.pop('items')
            
        quotation = SupplierQuotation.objects.create(**validate_data)
            
        for item_data in items_data:
            SupplierQuotationItem.objects.create(quotation=quotation, **item_data)
        
        self.calculate_totals(quotation)
        return quotation 
        
    @transaction.atomic
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        
        for field in ["rfq",
            "supplier",
            "quotation_number",
            "quotation_date",
            "valid_until",
            "notes"]:
            
            if field in validated_data:
                setattr(instance, field, validated_data[field])
                
        instance.save()
            
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                 SupplierQuotationItem.objects.create(quotation=instance, **item_data)
                    
        self.calculate_totals(instance)
        
        return instance
    
    def calculate_totals(self, quotation):
        subtotal = sum((item.subtotal for item in quotation.items.all()), Decimal('0'))
        tax = sum((item.tax for item in quotation.items.all()), Decimal('0'))
        quotation.subtotal = subtotal
        quotation.tax = tax
        quotation.grand_total = subtotal + tax
        quotation.save(update_fields=['subtotal', 'tax', 'grand_total', 'updated_at'])

class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderItem
        fields = ["id","product","quantity","unit_price","tax_rate","subtotal","tax","total","received_quantity",]
        read_only_fields = ["id","subtotal","tax","total","received_quantity",]
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError('Quantity must be greater than 0.')
        return value
    
class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True)
    
    class Meta:
        model = PurchaseOrder
        fields = [ "id","quotation","supplier","order_number","status","order_date","expected_date","notes","items","subtotal","tax","grand_total","created_at","updated_at"]
        read_only_fields = ["id","status","subtotal","tax","grand_total","created_at","updated_at"]
        
    def validate(self, attrs):
        quotation = attrs.get('quotation')
        supplier = attrs.get('supplier')
        
        if quotation and supplier:
            if quotation.supplier_id != supplier.id:
                 raise serializers.ValidationError({
                    "supplier": (
                        "Supplier must match quotation supplier."
                    )
                })
        
        if quotation:
            if quotation.status != 'ACCEPTED':
                 raise serializers.ValidationError({
                    "quotation": (
                        "Only accepted quotations "
                        "can create purchase orders."
                    )
                })
                
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        purchase_order = PurchaseOrder.objects.create(**validated_data)
        
        for item_data in items_data:
            PurchaseOrderItem.objects.create(purchase_order=purchase_order, **item_data)
            
        self.calculate_totals(purchase_order)
        return purchase_order
    
    @transaction.atomic
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        
        for field in [
            "quotation",
            "supplier",
            "order_number",
            "order_date",
            "expected_date",
            "notes",
        ]:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
                
        instance.save()
        
        if items_data is not None:
            instance.items.all().delete()
            
            for item_data in items_data:
                PurchaseOrderItem.objects.create(purchase_order=instance, **item_data)
        
        self.calculate_totals(instance)
        
        return instance
    
    def calculate_totals(self, order):
        subtotal = sum((item.subtotal for item in order.items.all()), Decimal('0'))
        tax = sum((item.tax for item in order.items.all()), Decimal('0'))
        
        order.subtotal = subtotal
        order.tax = tax
        order.grand_total = subtotal + tax
        
        order.save(update_fields=["subtotal","tax","grand_total","updated_at"])
        
class GoodsReceiptItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsReceiptItem
        fields = [ "id","purchase_order_item","received_quantity","notes"]
        read_only_fields = ["id"]
    
    def validate_received_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Received quantity must be greater than 0."
            )
        
        return value
    
class GoodsReceiptSerializer(serializers.ModelSerializer):
    items = GoodsReceiptItemSerializer(many=True)
    
    class Meta:
        model = GoodsReceipt
        fields = [ "id","purchase_order","receipt_number","status","received_date","notes","items","created_at","updated_at"]
        read_only_fields = ["id","status","created_at","updated_at"]
        
    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        purchase_order = validated_data[ "purchase_order"]
        
        if purchase_order.status not in [
            "APPROVED",
            "SENT",
            "PARTIALLY_RECEIVED"]:
            
            raise serializers.ValidationError({
                "purchase_order": (
                    "Purchase order cannot receive goods "
                    "in its current status."
                )
            })
            
        receipt = GoodsReceipt.objects.create(**validated_data)
        
        for item_data in items_data:
            po_item = item_data[  "purchase_order_item"]
            received_quantity = item_data["received_quantity"]
                        
            if po_item.purchase_order_id != purchase_order.id:
                raise serializers.ValidationError({
                    "purchase_order_item": (
                        "Item does not belong to this "
                        "purchase order."
                    )
                })
                
            remaining_quantity = (po_item.quantity - po_item.received_quantity)
            
            if received_quantity > remaining_quantity:
                raise serializers.ValidationError({
                    "received_quantity": (
                        f"Cannot receive more than "
                        f"remaining quantity "
                        f"({remaining_quantity})."
                    )
                })
                 
            GoodsReceiptItem.objects.create(goods_receipt=receipt, **item_data)
        
        return receipt