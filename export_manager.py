import csv
import json
import os
from datetime import datetime

class ExportManager:
    def __init__(self, export_dir='data/exports'):
        self.export_dir = export_dir
        os.makedirs(self.export_dir, exist_ok=True)
    
    def export_to_csv(self, data, filename_prefix='wallet_data'):
        if not data:
            return None
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.export_dir}/{filename_prefix}_{timestamp}.csv"
        
        if isinstance(data, dict):
            data = [data]
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if data:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            return filename
        except Exception as e:
            print(f"Error al exportar a CSV: {str(e)}")
            return None
    
    def export_to_json(self, data, filename_prefix='wallet_data'):
        if not data:
            return None
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.export_dir}/{filename_prefix}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return filename
        except Exception as e:
            print(f"Error al exportar a JSON: {str(e)}")
            return None
