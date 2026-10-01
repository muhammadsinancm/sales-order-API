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