#!/usr/bin/env python3
"""
Bitcoin Wallet Checker - Herramienta para verificar saldos y transacciones de billeteras cripto
"""
import sys
import os
import argparse
from datetime import datetime
from typing import Dict, Any, Optional

from Bitcoinwalletchecker import CryptoWalletChecker
from export_manager import ExportManager
from favorites_manager import FavoritesManager
from history_manager import HistoryManager
from wallet_analyzer import WalletAnalyzer
from price_alert import PriceAlert

class BitcoinWalletCheckerApp:
    def __init__(self):
        self.checker = CryptoWalletChecker()
        self.exporter = ExportManager()
        self.favorites = FavoritesManager()
        self.history = HistoryManager()
        self.analyzer = WalletAnalyzer()
        self.price_alert = PriceAlert()
        self.setup_argparse()
    
    def setup_argparse(self):
        """Configura el analizador de argumentos de línea de comandos"""
        self.parser = argparse.ArgumentParser(
            description='Bitcoin Wallet Checker - Verifica saldos y transacciones de billeteras cripto'
        )
        
        # Argumentos principales
        subparsers = self.parser.add_subparsers(dest='command', help='Comandos disponibles')
        
        # Comando: check
        check_parser = subparsers.add_parser('check', help='Verificar una dirección de billetera')
        check_parser.add_argument('address', help='Dirección de la billetera')
        check_parser.add_argument('--crypto', '-c', default='btc', 
                                choices=self.checker.config['cryptocurrencies'].keys(),
                                help='Tipo de criptomoneda')
        check_parser.add_argument('--export', '-e', choices=['json', 'csv'], 
                                help='Exportar resultados a archivo')
        
        # Comando: favorite
        fav_parser = subparsers.add_parser('favorite', help='Gestionar billeteras favoritas')
        fav_subparsers = fav_parser.add_subparsers(dest='fav_command')
        
        # Subcomandos para favoritos
        fav_add = fav_subparsers.add_parser('add', help='Añadir billetera a favoritos')
        fav_add.add_argument('name', help='Nombre para la billetera')
        fav_add.add_argument('address', help='Dirección de la billetera')
        fav_add.add_argument('--crypto', '-c', default='btc', 
                           choices=self.checker.config['cryptocurrencies'].keys(),
                           help='Tipo de criptomoneda')
        fav_add.add_argument('--notes', '-n', default='', help='Notas adicionales')
        
        fav_remove = fav_subparsers.add_parser('remove', help='Eliminar billetera de favoritos')
        fav_remove.add_argument('address', help='Dirección de la billetera a eliminar')
        
        fav_list = fav_subparsers.add_parser('list', help='Listar billeteras favoritas')
        
        # Comando: history
        hist_parser = subparsers.add_parser('history', help='Ver historial de búsquedas')
        hist_parser.add_argument('--limit', '-l', type=int, default=10, 
                               help='Número de entradas a mostrar')
        
        # Comando: alert
        alert_parser = subparsers.add_parser('alert', help='Gestionar alertas de precio')
        alert_subparsers = alert_parser.add_subparsers(dest='alert_command')
        
        alert_add = alert_subparsers.add_parser('add', help='Añadir alerta de precio')
        alert_add.add_argument('crypto', help='Símbolo de la criptomoneda')
        alert_add.add_argument('price', type=float, help='Precio objetivo')
        alert_add.add_argument('--condition', '-c', default='above', 
                             choices=['above', 'below'],
                             help='Condición de la alerta')
        
        alert_list = alert_subparsers.add_parser('list', help='Listar alertas activas')
        alert_remove = alert_subparsers.add_parser('remove', help='Eliminar alerta')
        alert_remove.add_argument('alert_id', type=int, help='ID de la alerta a eliminar')
    
    def run(self):
        """Ejecuta la aplicación según los argumentos proporcionados"""
        args = self.parser.parse_args()
        
        if not args.command:
            self.parser.print_help()
            return
        
        try:
            if args.command == 'check':
                self.handle_check(args)
            elif args.command == 'favorite':
                self.handle_favorite(args)
            elif args.command == 'history':
                self.handle_history(args)
            elif args.command == 'alert':
                self.handle_alert(args)
        except KeyboardInterrupt:
            print("\nOperación cancelada por el usuario.")
            sys.exit(1)
        except Exception as e:
            print(f"\nError: {str(e)}", file=sys.stderr)
            sys.exit(1)
    
    def handle_check(self, args):
        """Maneja el comando de verificación de billetera"""
        self.history.add_search(args.address, args.crypto)
        
        # Mostrar información básica
        data = self.checker.get_wallet_info(args.address, args.crypto)
        if 'error' in data:
            print(f"Error: {data['error']}")
            return
        
        # Mostrar información detallada
        self.checker.display_wallet_info(args.address, args.crypto)
        
        # Análisis adicional
        analysis = self.analyzer.analyze_wallet(data, args.crypto)
        print("\nAnálisis de la billetera:")
        for key, value in analysis.items():
            print(f"- {key}: {value}")
        
        # Exportar si se solicita
        if args.export:
            export_data = {
                'address': args.address,
                'crypto': args.crypto,
                'data': data,
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            }
            
            if args.export == 'json':
                filename = self.exporter.export_to_json(export_data, 
                    f"{args.crypto}_{args.address[:8]}_report")
            else:  # csv
                filename = self.exporter.export_to_csv([export_data], 
                    f"{args.crypto}_{args.address[:8]}_report")
            
            if filename:
                print(f"\nDatos exportados a: {filename}")
    
    def handle_favorite(self, args):
        """Maneja los comandos de favoritos"""
        if args.fav_command == 'add':
            if self.favorites.add_favorite(args.name, args.address, args.crypto, args.notes):
                print(f"Billetera {args.name} añadida a favoritos.")
            else:
                print("La billetera ya está en favoritos.")
        
        elif args.fav_command == 'remove':
            if self.favorites.remove_favorite(args.address):
                print("Billetera eliminada de favoritos.")
            else:
                print("Billetera no encontrada en favoritos.")
        
        elif args.fav_command == 'list':
            favorites = self.favorites.get_favorites()
            if not favorites:
                print("No hay billeteras en favoritos.")
                return
                
            print("\nBilleteras favoritas:")
            print("-" * 80)
            for addr, fav in favorites.items():
                print(f"Nombre: {fav['name']}")
                print(f"Dirección: {addr}")
                print(f"Cripto: {fav['crypto'].upper()}")
                if fav.get('notes'):
                    print(f"Notas: {fav['notes']}")
                print("-" * 80)
    
    def handle_history(self, args):
        """Muestra el historial de búsquedas"""
        history = self.history.get_recent_searches(args.limit)
        if not history:
            print("No hay historial de búsquedas.")
            return
            
        print("\nHistorial de búsquedas recientes:")
        print("-" * 80)
        for i, item in enumerate(history, 1):
            dt = datetime.fromisoformat(item['timestamp'])
            print(f"{i}. {dt.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Dirección: {item['address']}")
            print(f"   Cripto: {item['crypto'].upper()}")
            print("-" * 80)
    
    def handle_alert(self, args):
        """Maneja los comandos de alertas de precio"""
        if args.alert_command == 'add':
            alert_id = self.price_alert.add_alert(
                args.crypto, 
                args.price, 
                args.condition
            )
            print(f"Alerta {alert_id} creada: {args.crypto.upper()} {args.condition} {args.price}")
        
        elif args.alert_command == 'list':
            alerts = self.price_alert.get_alerts()
            if not alerts:
                print("No hay alertas activas.")
                return
                
            print("\nAlertas activas:")
            print("-" * 80)
            for alert_id, alert in alerts.items():
                print(f"ID: {alert_id}")
                print(f"Cripto: {alert['crypto'].upper()}")
                print(f"Precio: {alert['price']} {alert['condition']}")
                print(f"Creada: {alert['created_at']}")
                print("-" * 80)
        
        elif args.alert_command == 'remove':
            if self.price_alert.remove_alert(args.alert_id):
                print(f"Alerta {args.alert_id} eliminada.")
            else:
                print("Alerta no encontrada.")

def main():
    """Función principal"""
    try:
        app = BitcoinWalletCheckerApp()
        app.run()
    except KeyboardInterrupt:
        print("\nAplicación finalizada por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError inesperado: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
