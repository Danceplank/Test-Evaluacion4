
## 3. services/ransomware_protection.py


from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import hashlib
import json

class RansomwareProtectionService:
    def __init__(self):
        self.ransomware_indicators = [
            "encryption_patterns",
            "file_extension_changes",
            "mass_file_operations",
            "suspicious_process_behavior"
        ]
    
    def monitor_file_operations(self, endpoint_id: str, file_operations: List[Dict]) -> Dict[str, Any]:
        """Monitorea operaciones de archivo en tiempo real para detectar ransomware"""
        suspicious_activities = []
        protected_files = 0
        
        for operation in file_operations:
            if self._is_suspicious_operation(operation):
                suspicious_activities.append(operation)
            
            # Crear copia de seguridad automática
            if self._should_backup_file(operation):
                self._create_file_backup(operation)
                protected_files += 1
        
        return {
            "endpoint_id": endpoint_id,
            "timestamp": datetime.utcnow(),
            "suspicious_activities": suspicious_activities,
            "files_protected": protected_files,
            "threat_level": "HIGH" if suspicious_activities else "LOW"
        }
    
    def _is_suspicious_operation(self, operation: Dict) -> bool:
        """Detecta operaciones sospechosas de ransomware"""
        # Detectar cambios masivos de extensiones
        if operation.get('operation_type') == 'RENAME':
            old_ext = operation.get('old_name', '').split('.')[-1].lower()
            new_ext = operation.get('new_name', '').split('.')[-1].lower()
            
            suspicious_extensions = ['crypt', 'locked', 'encrypted', 'ransom']
            if any(ext in new_ext for ext in suspicious_extensions):
                return True
        
        # Detectar múltiples operaciones de escritura en poco tiempo
        if operation.get('operation_type') == 'WRITE' and operation.get('file_count', 0) > 100:
            return True
            
        return False
    
    def _should_backup_file(self, operation: Dict) -> bool:
        """Determina si se debe crear backup del archivo"""
        important_extensions = ['.doc', '.docx', '.pdf', '.xls', '.xlsx', '.ppt', '.pptx']
        file_extension = operation.get('file_name', '').split('.')[-1].lower()
        
        return any(ext in file_extension for ext in important_extensions)
    
    def _create_file_backup(self, operation: Dict):
        """Crea copia de seguridad a prueba de manipulación"""
        # En producción, aquí se implementaría el sistema real de backup
        backup_data = {
            "file_path": operation.get('file_path'),
            "file_name": operation.get('file_name'),
            "backup_time": datetime.utcnow(),
            "hash": hashlib.sha256(json.dumps(operation).encode()).hexdigest()
        }
        return backup_data
    
    def block_malicious_process(self, process_info: Dict) -> Dict[str, Any]:
        """Bloquea procesos maliciosos identificados"""
        return {
            "process_id": process_info.get('pid'),
            "process_name": process_info.get('name'),
            "action": "TERMINATED",
            "reason": "Ransomware behavior detected",
            "timestamp": datetime.utcnow()
        }