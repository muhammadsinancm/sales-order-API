from .models import AuditLog

def create_audit_log(user, action, entity_type, entity_id, details=None):
    return AuditLog.objects.create(user=user, action=action, entity_type=entity_type, entity_id=entity_id, details=details or {})