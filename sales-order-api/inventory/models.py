from django.db import models
from products.models import Product

class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory')
    quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
    
class StockTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('IN', 'Stock In'), ('OUT', 'Stock Out')
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_transactions')
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return (f"{self.product.name} - " 
                f"{self.transaction_typ} - " 
                f"{self.quantity}")