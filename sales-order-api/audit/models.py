from django.db import models
from django.contrib.auth.models import User

class AuditLog(models.Model):
    ACTION_CHOICES = [
        # Sales Order
        ('ORDER_CONFIRMED', 'Order Confirmed'),
        ('ORDER_CANCELLED', 'Order Cancelled'),
        ('ORDER_PROCESSING', 'Order Processing'),
        ('ORDER_COMPLETED', 'Order Completed'),
        
        # Supplier / RFQ
        ("RFQ_SENT", "RFQ Sent"),
        ("RFQ_CANCELLED", "RFQ Cancelled"),

       # Supplier Quotation
       ("QUOTATION_SENT", "Quotation Sent"),
       ("QUOTATION_ACCEPTED", "Quotation Accepted"),
       ("QUOTATION_REJECTED", "Quotation Rejected"),
       ("QUOTATION_CANCELLED", "Quotation Cancelled"),

       # Purchase Order
       ("PURCHASE_ORDER_APPROVED", "Purchase Order Approved"),
       ("PURCHASE_ORDER_SENT", "Purchase Order Sent"),
       ("PURCHASE_ORDER_CANCELLED", "Purchase Order Cancelled"),

       # Goods Receipt
       ("GOODS_RECEIVED", "Goods Received"),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    entity_type = models.CharField(max_length=50)
    entity_id = models.PositiveIntegerField()
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.action} - {self.entity_type} #{self.entity_id}"