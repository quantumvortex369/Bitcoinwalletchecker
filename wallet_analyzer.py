"""
Módulo para análisis avanzado de billeteras cripto
"""
from datetime import datetime
from typing import Dict, Any
import requests

class WalletAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    def analyze_wallet(self, wallet_data: Dict[str, Any], crypto: str) -> Dict[str, Any]:
        """
        Realiza un análisis detallado de una billetera
        
        Args:
            wallet_data: Datos de la billetera
            crypto: Símbolo de la criptomoneda (btc, eth, etc.)
            
        Returns:
            Dict con el análisis realizado
        """
        analysis = {}
        
        # Análisis básico
        balance = wallet_data.get('final_balance', 0)
        total_received = wallet_data.get('total_received', 0)
        n_tx = wallet_data.get('n_tx', 0)
        
        # Calcular actividad
        analysis['Saldo actual'] = self._format_balance(balance, crypto)
        analysis['Total recibido'] = self._format_balance(total_received, crypto)
        analysis['Número de transacciones'] = n_tx
        
        # Calcular actividad reciente
        if 'unconfirmed_tx_n' in wallet_data:
            analysis['Transacciones no confirmadas'] = wallet_data['unconfirmed_tx_n']
        
        # Determinar tipo de billetera
        analysis['Tipo de billetera'] = self._determine_wallet_type(wallet_data, crypto)
        
        # Calcular actividad mensual
        if n_tx > 0:
            first_seen = wallet_data.get('first_tx', {}).get('time', 0)
            if first_seen:
                months_active = self._calculate_months_active(first_seen)
                if months_active > 0:
                    tx_per_month = n_tx / months_active
                    analysis['Transacciones/mes'] = f"{tx_per_month:.1f}"
        
        # Análisis de riesgo básico
        risk_factors = []
        if n_tx == 0:
            risk_factors.append("Billetera inactiva")
        if balance == 0 and total_received > 0:
            risk_factors.append("Billetera vaciada")
        
        if risk_factors:
            analysis['Factores de riesgo'] = ", ".join(risk_factors)
        
        return analysis
    
    def _format_balance(self, satoshis: int, crypto: str) -> str:
        """Formatea el balance según la criptomoneda"""
        if crypto == 'btc' or crypto == 'ltc':
            return f"{satoshis / 1e8:.8f} {crypto.upper()}"
        elif crypto == 'eth':
            return f"{satoshis / 1e18:.8f} {crypto.upper()}"
        return f"{satoshis} {crypto.upper()}"
    
    def _determine_wallet_type(self, wallet_data: Dict[str, Any], crypto: str) -> str:
        """Intenta determinar el tipo de billetera"""
        n_tx = wallet_data.get('n_tx', 0)
        total_received = wallet_data.get('total_received', 0)
        
        if n_tx == 0:
            return "Billetera nueva"
        elif n_tx > 1000 or total_received > 1e8:  # Ajustar según la criptomoneda
            return "Billetera de intercambio o institucional"
        elif n_tx > 100:
            return "Billetera de uso frecuente"
        else:
            return "Billetera de uso personal"
    
    def _calculate_months_active(self, first_seen_timestamp: int) -> int:
        """Calcula cuántos meses ha estado activa la billetera"""
        try:
            first_seen = datetime.fromtimestamp(first_seen_timestamp)
            now = datetime.now()
            months = (now.year - first_seen.year) * 12 + (now.month - first_seen.month)
            return max(1, months)  # Mínimo 1 mes para evitar división por cero
        except (TypeError, ValueError):
            return 1
