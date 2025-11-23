from typing import List, Dict, Any
from datetime import datetime

class NetworkAttackDefenseService:
    def __init__(self):
        self.network_threats = [
            "port_scanning",
            "brute_force_attempts",
            "vulnerability_exploitation",
            "suspicious_traffic"
        ]
    
    def analyze_network_traffic(self, traffic_data: Dict) -> Dict[str, Any]:
        """Analiza tráfico de red en busca de ataques"""
        threats_detected = []
        blocked_connections = 0
        
        for packet in traffic_data.get('packets', []):
            threat_analysis = self._analyze_packet(packet)
            if threat_analysis.get('is_threat'):
                threats_detected.append(threat_analysis)
                blocked_connections += 1
        
        return {
            "analysis_time": datetime.utcnow(),
            "threats_detected": threats_detected,
            "connections_blocked": blocked_connections,
            "recommended_actions": self._get_network_recommendations(threats_detected)
        }
    
    def _analyze_packet(self, packet: Dict) -> Dict[str, Any]:
        """Analiza paquetes individuales en busca de amenazas"""
        # Detectar escaneo de puertos
        if self._is_port_scan(packet):
            return {
                "is_threat": True,
                "threat_type": "PORT_SCANNING",
                "severity": "MEDIUM",
                "action": "BLOCKED"
            }
        
        # Detectar intentos de fuerza bruta
        if self._is_brute_force(packet):
            return {
                "is_threat": True,
                "threat_type": "BRUTE_FORCE",
                "severity": "HIGH",
                "action": "BLOCKED"
            }
        
        return {"is_threat": False}
    
    def _is_port_scan(self, packet: Dict) -> bool:
        """Detecta patrones de escaneo de puertos"""
        # Lógica simplificada para detección
        return packet.get('flags', {}).get('syn', False) and not packet.get('flags', {}).get('ack', False)
    
    def _is_brute_force(self, packet: Dict) -> bool:
        """Detecta patrones de fuerza bruta"""
        # Lógica simplificada para detección
        return (packet.get('protocol') == 'SSH' or packet.get('protocol') == 'RDP') and packet.get('attempt_count', 0) > 5
    
    def _get_network_recommendations(self, threats: List[Dict]) -> List[str]:
        """Genera recomendaciones basadas en amenazas detectadas"""
        recommendations = []
        
        if any(t['threat_type'] == 'PORT_SCANNING' for t in threats):
            recommendations.append("Reforzar reglas de firewall para puertos sensibles")
        
        if any(t['threat_type'] == 'BRUTE_FORCE' for t in threats):
            recommendations.append("Implementar autenticación multi-factor")
            recommendations.append("Limitar intentos de conexión")
        
        return recommendations