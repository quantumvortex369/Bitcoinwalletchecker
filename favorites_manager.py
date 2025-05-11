import json
import os

class FavoritesManager:
    def __init__(self, favorites_file='data/favorites/favorites.json'):
        self.favorites_file = favorites_file
        self.favorites = self._load_favorites()
    
    def _load_favorites(self):
        if not os.path.exists(self.favorites_file):
            os.makedirs(os.path.dirname(self.favorites_file), exist_ok=True)
            return {}
        
        try:
            with open(self.favorites_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def add_favorite(self, name, address, crypto, notes=''):
        if address in self.favorites:
            return False
            
        self.favorites[address] = {
            'name': name,
            'crypto': crypto,
            'notes': notes,
            'created_at': datetime.now().isoformat()
        }
        self._save_favorites()
        return True
    
    def remove_favorite(self, address):
        if address in self.favorites:
            del self.favorites[address]
            self._save_favorites()
            return True
        return False
    
    def get_favorites(self):
        return self.favorites
    
    def _save_favorites(self):
        with open(self.favorites_file, 'w') as f:
            json.dump(self.favorites, f, indent=2)
