import pandas as pd
import os

class DataService:
    def __init__(self):
        self.parquet_path = "backend/data/zomato.parquet"
        self.df = None
        self._load_data()

    def _load_data(self):
        if not os.path.exists(self.parquet_path):
            print(f"Error: {self.parquet_path} not found.")
            return

        print(f"Loading data from {self.parquet_path}...")
        try:
            full_df = pd.read_parquet(self.parquet_path)
            
            # --- 1. Deduplication ---
            # Remove duplicates based on name and address
            self.df = full_df.drop_duplicates(subset=['name', 'address'], keep='first').copy()
            
            # --- 2. Data Cleaning & Normalization ---
            self.df['rating_numeric'] = self.df['rate'].apply(self._parse_rating)
            
            # Normalize Locations (Group Koramangala, HSR, etc.)
            self.df['location'] = self.df['location'].fillna('').apply(self._normalize_location)
            
            cost_col = 'approx_cost(for two people)'
            if cost_col in self.df.columns:
                self.df['cost_numeric'] = pd.to_numeric(self.df[cost_col].str.replace(',', ''), errors='coerce')
            
            self.df['cuisines'] = self.df['cuisines'].fillna('')
            self.df['address'] = self.df['address'].fillna('')
            
            print(f"Data ready. Total unique restaurants: {len(self.df)}")
        except Exception as e:
            print(f"Failed to load data: {e}")
            raise e

    def _normalize_location(self, loc):
        if not loc: return ""
        # Group sub-blocks/sectors into parent locality
        parents = [
            "Koramangala", "HSR", "Jayanagar", "JP Nagar", 
            "Banashankari", "BTM", "Indiranagar", "Malleshwaram",
            "Rajajinagar", "Whitefield", "Marathahalli", "Bellandur"
        ]
        for p in parents:
            if p.lower() in loc.lower():
                return p
        return loc

    def _parse_rating(self, rate_str):
        if not rate_str or not isinstance(rate_str, str) or rate_str == 'NEW' or rate_str == '-':
            return 0.0
        try:
            # Handle "4.1/5"
            return float(rate_str.split('/')[0].strip())
        except:
            return 0.0

    def filter_restaurants(self, location=None, selected_cuisines=None, min_rating=None, price_range=None, limit=15):
        if self.df is None:
            return []

        filtered = self.df.copy()

        # Location (Required)
        if location:
            filtered = filtered[filtered['location'] == location]
        
        # Price Range (Required)
        if price_range:
            if price_range == "Under ₹500":
                filtered = filtered[filtered['cost_numeric'] < 500]
            elif price_range == "₹500 - ₹1500":
                filtered = filtered[(filtered['cost_numeric'] >= 500) & (filtered['cost_numeric'] <= 1500)]
            elif price_range == "Above ₹1500":
                filtered = filtered[filtered['cost_numeric'] > 1500]
            
        # Cuisine Logic (Optional: Match any of selected)
        if selected_cuisines and len(selected_cuisines) > 0:
            # Check if any of the selected cuisines are in the restaurant's cuisine list
            pattern = '|'.join(selected_cuisines)
            filtered = filtered[filtered['cuisines'].str.contains(pattern, case=False, na=False)]
            
        # Rating (Optional)
        if min_rating is not None:
            filtered = filtered[filtered['rating_numeric'] >= min_rating]
            
        # Sort by rating and votes to get best candidates
        results = filtered.sort_values(by=['rating_numeric', 'votes'], ascending=False).head(limit)
        
        return results.to_dict(orient='records')

    def get_unique_locations(self):
        if self.df is None: return []
        # Locations that have at least one restaurant
        return sorted([loc for loc in self.df['location'].unique() if loc])

    def get_unique_cuisines(self):
        if self.df is None: return []
        all_cuisines = set()
        self.df['cuisines'].str.split(', ').apply(lambda x: [all_cuisines.add(c) for c in x if isinstance(x, list)])
        return sorted([c for c in all_cuisines if c])

# Singleton instance
data_service = None

def get_data_service():
    global data_service
    if data_service is None:
        data_service = DataService()
    return data_service
