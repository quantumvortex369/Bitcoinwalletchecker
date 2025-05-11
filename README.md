# Bitcoin Wallet Checker

Una herramienta de línea de comandos para verificar saldos y transacciones de billeteras de criptomonedas.

## Características

- Verificación de saldos en múltiples criptomonedas (BTC, ETH, LTC, DOGE, etc.)
- Análisis detallado de billeteras
- Sistema de alertas de precios
- Historial de búsquedas
- Favoritos
- Exportación de datos (JSON, CSV)

## Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/quantumvortex369/Bitcoinwalletchecker
   cd BitcoinWalletChecker
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

### Verificar una billetera
```bash
python main.py check [DIRECCIÓN] --crypto [CRIPTOMONEDA] --export [FORMATO]
```

Ejemplo:
```bash
python main.py check 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa --crypto btc --export json
```

### Gestión de favoritos
- Añadir a favoritos:
  ```bash
  python main.py favorite add [NOMBRE] [DIRECCIÓN] --crypto [CRIPTOMONEDA] --notes [NOTAS]
  ```
  
- Listar favoritos:
  ```bash
  python main.py favorite list
  ```
  
- Eliminar de favoritos:
  ```bash
  python main.py favorite remove [DIRECCIÓN]
  ```

### Historial de búsquedas
```bash
python main.py history [--limit N]
```

### Alertas de precios
- Crear alerta:
  ```bash
  python main.py alert add [CRIPTO] [PRECIO] --condition [above|below] --note [NOTA]
  ```
  
- Listar alertas:
  ```bash
  python main.py alert list
  ```
  
- Eliminar alerta:
  ```bash
  python main.py alert remove [ID_ALERTA]
  ```

## Configuración

El archivo `config.json` contiene la configuración de la aplicación:
- Criptomonedas soportadas
- Monedas fíat para conversión
- Configuración de la API
- Configuración de temas

## Contribución

Las contribuciones son bienvenidas. Por favor, envía un Pull Request con tus mejoras.
