"""
Módulo para gestionar alertas de precios de criptomonedas
"""
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import requests

class PriceAlert:
    def __init__(self, alerts_file: str = 'data/price_alerts.json'):
        """
        Inicializa el gestor de alertas de precios
        
        Args:
            alerts_file: Ruta al archivo donde se guardarán las alertas
        """
        self.alerts_file = alerts_file
        self.alerts = self._load_alerts()
        self.next_alert_id = max(self.alerts.keys(), default=0) + 1
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    def _load_alerts(self) -> Dict[int, dict]:
        """Carga las alertas desde el archivo"""
        if not os.path.exists(self.alerts_file):
            os.makedirs(os.path.dirname(self.alerts_file), exist_ok=True)
            return {}
        
        try:
            with open(self.alerts_file, 'r') as f:
                return {int(k): v for k, v in json.load(f).items()}
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_alerts(self):
        """Guarda las alertas en el archivo"""
        with open(self.alerts_file, 'w') as f:
            json.dump(self.alerts, f, indent=2)
    
    def add_alert(self, crypto: str, price: float, condition: str = 'above', 
                 note: str = '') -> int:
        """
        Añade una nueva alerta de precio
        
        Args:
            crypto: Símbolo de la criptomoneda (ej: 'btc')
            price: Precio objetivo
            condition: 'above' o 'below' para indicar si se alerta cuando el precio
                     esté por encima o por debajo del objetivo
            note: Nota opcional para la alerta
            
        Returns:
            ID de la alerta creada
        """
        alert_id = self.next_alert_id
        self.next_alert_id += 1
        
        self.alerts[alert_id] = {
            'crypto': crypto.lower(),
            'price': float(price),
            'condition': condition.lower(),
            'note': note,
            'created_at': datetime.now().isoformat(),
            'triggered': False
        }
        
        self._save_alerts()
        return alert_id
    
    def remove_alert(self, alert_id: int) -> bool:
        """
        Elimina una alerta
        
        Args:
            alert_id: ID de la alerta a eliminar
            
        Returns:
            True si la alerta existía y fue eliminada, False en caso contrario
        """
        if alert_id in self.alerts:
            del self.alerts[alert_id]
            self._save_alerts()
            return True
        return False
    
    def get_alerts(self, include_triggered: bool = False) -> Dict[int, dict]:
        """
        Obtiene todas las alertas
        
        Args:
            include_triggered: Si es True, incluye las alertas ya activadas
            
        Returns:
            Diccionario con las alertas
        """
        if include_triggered:
            return self.alerts.copy()
        return {k: v for k, v in self.alerts.items() if not v['triggered']}
    
    def check_alerts(self) -> List[Tuple[int, dict]]:
        """
        Comprueba si alguna alerta debe activarse
        
        Returns:
            Lista de tuplas (alert_id, alert_data) de las alertas activadas
        """
        triggered = []
        
        for alert_id, alert in self.alerts.items():
            if alert['triggered']:
                continue
                
            current_price = self._get_current_price(alert['crypto'])
            if current_price is None:
                continue
                
            price_condition_met = (
                (alert['condition'] == 'above' and current_price >= alert['price']) or
                (alert['condition'] == 'below' and current_price <= alert['price'])
            )
            
            if price_condition_met:
                alert['triggered'] = True
                alert['triggered_at'] = datetime.now().isoformat()
                alert['triggered_price'] = current_price
                triggered.append((alert_id, alert))
        
        if triggered:
            self._save_alerts()
            
        return triggered
    
    def _get_current_price(self, crypto: str) -> Optional[float]:
        """
        Obtiene el precio actual de una criptomoneda
        
        Args:
            crypto: Símbolo de la criptomoneda
            
        Returns:
            Precio actual o None si no se pudo obtener
        """
        try:
            # Usar CoinGecko API para obtener precios
            response = self.session.get(
                f'https://api.coingecko.com/api/v3/coins/{crypto}?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=false'
            )
            response.raise_for_status()
            data = response.json()
            return data['market_data']['current_price']['usd']
        except (requests.RequestException, KeyError, ValueError):
            return None

# Ejemplo de uso:
if __name__ == "__main__":
    # Crear una instancia del gestor de alertas
    alert_manager = PriceAlert()
    
    # Añadir una alerta para cuando el BTC supere los 50,000 USD
    alert_id = alert_manager.add_alert(
        crypto='bitcoin',
        price=50000,
        condition='above',
        note='Alerta de precio alto de BTC'
    )
    print(f"Alerta creada con ID: {alert_id}")
    
    # Comprobar alertas (normalmente se haría en un bucle periódico)
    triggered = alert_manager.check_alerts()
    for alert_id, alert in triggered:
        print(f"¡Alerta activada! {alert['crypto'].upper()} ha alcanzado {alert['price']} USD")
    
    # Listar alertas activas
    print("\nAlertas activas:")
    for alert_id, alert in alert_manager.get_alerts().items():
        print(f"ID: {alert_id}, {alert['crypto'].upper()} {alert['condition']} {alert['price']} USD")
