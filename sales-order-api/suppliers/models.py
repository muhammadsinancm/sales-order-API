from django.db import models
from products.models import Product

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class RequestForQuotation(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('RECEIVED', 'Received'),
        ('CANCELLED', 'Cancelled')
    ]
    
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='rfqs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    quotation_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"RFQ #{self.id}"

class RFQItem(models.Model):
    rfq = models.ForeignKey(RequestForQuotation, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='req_items')
    quantity = models.PositiveIntegerField()
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

class SupplierQuotation(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled')
    ]
    
    rfq = models.ForeignKey(RequestForQuotation, on_delete=models.CASCADE, related_name='quotations')
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='quotations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    quotation_number = models.CharField(max_length=100, unique=True)
    quotation_date = models.DateField()
    valid_until = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.quotation_number
    
class SupplierQuotationItem(models.Model):
    quotation = models.ForeignKey(SupplierQuotation, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='supplier_quotation_items')
    quantity = models.PositiveBigIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    tax = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    total = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    
    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        self.tax = (self.subtotal * self.tax_rate) / 100
        self.total = self.subtotal + self.tax
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.product.name} - {self.quotation.quotation_number}"
    
class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("APPROVED", "Approved"),
        ("SENT", "Sent"),
        ("PARTIALLY_RECEIVED", "Partially Received"),
        ("RECEIVED", "Received"),
        ("CANCELLED", "Cancelled"),
    ]
    
    quotation = models.ForeignKey(SupplierQuotation, on_delete=models.PROTECT,  related_name="purchase_orders")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT,  related_name="purchase_orders")
    order_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='DRAFT')
    order_date = models.DateField()
    expected_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12,decimal_places=2,default=0)
    grand_total = models.DecimalField(max_digits=12,decimal_places=2,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.order_number
    
class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder,on_delete=models.CASCADE,related_name="items")
    product = models.ForeignKey(Product,on_delete=models.PROTECT,related_name="purchase_order_items")
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12,decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5,decimal_places=2,default=0)
    subtotal = models.DecimalField(max_digits=12,decimal_places=2,default=0)
    tax = models.DecimalField(max_digits=12,decimal_places=2,default=0)
    total = models.DecimalField(max_digits=12,decimal_places=2,default=0)
    received_quantity = models.PositiveIntegerField(default=0)
    
    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        self.tax = (self.subtotal * self.tax_rate) / 100
        self.total = self.subtotal + self.tax
        super().save(*args, **kwargs)
    
    def __str__(self):
        return (
            f"{self.product.name} - "
            f"{self.purchase_order.order_number}"
        )

class GoodsReceipt(models.Model):
    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("RECEIVED", "Received"),
        ("CANCELLED", "Cancelled"),
    ]

    purchase_order = models.ForeignKey(PurchaseOrder,on_delete=models.PROTECT,related_name="goods_receipts")
    receipt_number = models.CharField(max_length=100,unique=True)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="DRAFT")
    received_date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.receipt_number
    
class GoodReceiptItem(models.Model):
    goods_receipt = models.ForeignKey(GoodsReceipt,on_delete=models.CASCADE,related_name="items")
    purchase_order_item = models.ForeignKey(PurchaseOrderItem,on_delete=models.PROTECT,related_name="receipt_items")
    received_quantity = models.PositiveIntegerField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return (
            f"{self.purchase_order_item.product.name} - "
            f"{self.received_quantity}"
        )