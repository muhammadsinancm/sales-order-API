from rest_framework import serializers
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'action', 'entity_type', 'entity_id', 'details', 'created_at'
        ]
        
        read_only_fields = [
            'id', 'user', 'action', 'entity_type', 'entity_id', 'details', 'created_at'
        ]