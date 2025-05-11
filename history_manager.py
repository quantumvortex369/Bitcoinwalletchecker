import json
import os
from datetime import datetime

class HistoryManager:
    def __init__(self, history_file='data/history/history.json'):
        self.history_file = history_file
        self.history = self._load_history()
    
    def _load_history(self):
        if not os.path.exists(self.history_file):
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            return []
        
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def add_search(self, address, crypto):
        search = {
            'address': address,
            'crypto': crypto,
            'timestamp': datetime.now().isoformat()
        }
        self.history.insert(0, search)
        self._save_history()
    
    def get_recent_searches(self, limit=10):
        return self.history[:limit]
    
    def clear_history(self):
        self.history = []
        self._save_history()
    
    def _save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
