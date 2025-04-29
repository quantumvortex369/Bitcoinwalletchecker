import requests

def check_wallet(address):
    url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}"
    response = requests.get(url)

    if response.status_code != 200:
        print("❌ Dirección no válida o error en la API.")
        return

    data = response.json()
    
    balance_btc = data['final_balance'] / 1e8
    total_received = data['total_received'] / 1e8
    txs = data['n_tx']

    print(f"📬 Dirección: {address}")
    print(f"💰 Balance actual: {balance_btc} BTC")
    print(f"📥 Total recibido: {total_received} BTC")
    print(f"🔁 Número de transacciones: {txs}")

# Ejemplo de uso
address = input("🔎 Ingresa la dirección BTC: ")
check_wallet(address)