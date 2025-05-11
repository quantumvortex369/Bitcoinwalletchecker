import requests
import json
from datetime import datetime

class CryptoWalletChecker:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
        self.fiat_rates = {}
        self.load_config()
        self.update_fiat_rates()

    def load_config(self):
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                'cryptocurrencies': {
                    'btc': {'name': 'Bitcoin', 'api_url': 'https://api.blockcypher.com/v1/btc/main'},
                    'eth': {'name': 'Ethereum', 'api_url': 'https://api.blockcypher.com/v1/eth/main'},
                    'ltc': {'name': 'Litecoin', 'api_url': 'https://api.blockcypher.com/v1/ltc/main'}
                },
                'fiat_currencies': ['usd', 'eur', 'gbp']
            }
            with open('config.json', 'w') as f:
                json.dump(self.config, f, indent=4)

    def update_fiat_rates(self):
        try:
            response = self.session.get('https://api.coingecko.com/api/v3/exchange_rates')
            response.raise_for_status()
            data = response.json()
            self.fiat_rates = {
                'usd': data['rates']['usd']['value'],
                'eur': data['rates']['eur']['value'],
                'gbp': data['rates']['gbp']['value']
            }
        except Exception as e:
            print(f"Warning: No se pudieron obtener las tasas de cambio: {str(e)}")

    def validate_address(self, address, crypto):
        # Validación básica de direcciones
        if crypto == 'btc':
            return len(address) in [25, 34] and address[0] in ['1', '3', 'bc1']
        elif crypto == 'eth':
            return address.startswith('0x') and len(address) == 42
        elif crypto == 'ltc':
            return address.startswith(('L', 'M', '3')) and len(address) in [26, 34]
        return False

    def get_wallet_info(self, address, crypto='btc'):
        if not self.validate_address(address, crypto):
            return {"error": f"Dirección {crypto.upper()} no válida"}

        try:
            url = f"{self.config['cryptocurrencies'][crypto]['api_url']}/addrs/{address}"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error al conectarse a la API: {str(e)}"}

    def format_balance(self, satoshis, crypto):
        if crypto == 'btc' or crypto == 'ltc':
            return satoshis / 1e8
        elif crypto == 'eth':
            return satoshis / 1e18
        return satoshis

    def convert_to_fiat(self, amount, crypto):
        if not self.fiat_rates:
            return {}
        return {fiat: amount * self.fiat_rates.get(fiat, 0) for fiat in self.config['fiat_currencies']}

    def display_wallet_info(self, address, crypto='btc'):
        data = self.get_wallet_info(address, crypto)
        
        if 'error' in data:
            print(f"Error: {data['error']}")
            return

        crypto_name = self.config['cryptocurrencies'][crypto]['name']
        balance = self.format_balance(data['final_balance'], crypto)
        total_received = self.format_balance(data['total_received'], crypto)
        fiat_values = self.convert_to_fiat(balance, crypto)
        
        print("\n" + "="*60)
        print(f"Información de la billetera {crypto_name.upper()}")
        print("="*60)
        print(f"Dirección: {address}")
        print(f"Balance actual: {balance:.8f} {crypto.upper()}")
        
        if fiat_values:
            print("\nValor en otras monedas:")
            for currency, value in fiat_values.items():
                print(f"- {value:,.2f} {currency.upper()}")
        
        print(f"\nTotal recibido: {total_received:.8f} {crypto.upper()}")
        print(f"Número de transacciones: {data['n_tx']}")
        print(f"Última transacción: {datetime.fromtimestamp(data['unconfirmed_tx_n'] if 'unconfirmed_tx_n' in data else 0)}")
        print("="*60 + "\n")

def main():
    checker = CryptoWalletChecker()
    
    while True:
        print("\n" + "="*40)
        print("  VERIFICADOR DE BILLETERAS CRIPTO  ")
        print("="*40)
        print("Criptomonedas soportadas:")
        for i, (crypto, info) in enumerate(checker.config['cryptocurrencies'].items(), 1):
            print(f"{i}. {info['name']} ({crypto.upper()})")
        print("0. Salir")
        
        try:
            choice = int(input("\nSeleccione una opción: "))
            if choice == 0:
                break
                
            crypto = list(checker.config['cryptocurrencies'].keys())[choice-1]
            address = input(f"\nIngrese la dirección {checker.config['cryptocurrencies'][crypto]['name']}: ").strip()
            checker.display_wallet_info(address, crypto)
            
            input("\nPresione Enter para continuar...")
        except (ValueError, IndexError):
            print("\nOpción no válida. Por favor, intente de nuevo.")
        except KeyboardInterrupt:
            print("\nSaliendo del programa...")
            break

if __name__ == "__main__":
    main()
