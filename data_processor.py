import pandas as pd
import os
import logging
from urllib.parse import quote
import re
from datetime import datetime

class BankDataProcessor:
    def __init__(self, excel_file='bank_data.xlsx'):
        self.excel_file = excel_file
        self.data = None
        self.load_data()
        
    def load_data(self):
        """Load data from Excel file"""
        try:
            if os.path.exists(self.excel_file):
                self.data = pd.read_excel(self.excel_file)
                # Ensure consistent column names
                self.data.columns = self.data.columns.str.strip()
                # Fill NaN values with empty strings
                self.data = self.data.fillna('')
                logging.info(f"Loaded {len(self.data)} records from {self.excel_file}")
            else:
                logging.warning(f"Excel file {self.excel_file} not found. Using empty dataset.")
                # Create empty DataFrame with expected columns
                self.data = pd.DataFrame(columns=['Bank Name', 'City', 'Branch', 'IFSC', 'MICR', 'Address', 'State'])
        except Exception as e:
            logging.error(f"Error loading data: {e}")
            self.data = pd.DataFrame(columns=['Bank Name', 'City', 'Branch', 'IFSC', 'MICR', 'Address', 'State'])
    
    def create_slug(self, text):
        """Create URL-friendly slug from text"""
        if not text:
            return ""
        slug = re.sub(r'[^a-zA-Z0-9\s]', '', str(text).lower())
        slug = re.sub(r'\s+', '-', slug)
        return slug.strip('-')
    
    def search(self, query, search_type='auto'):
        """Search for bank information based on query and type"""
        if self.data is None or len(self.data) == 0:
            return []
        
        query = query.strip().upper()
        results = []
        
        if search_type == 'auto':
            # Auto-detect search type based on query format
            if len(query) == 11 and query.isalnum():
                search_type = 'ifsc'
            elif query.isdigit() and len(query) >= 9:
                search_type = 'micr'
            else:
                search_type = 'bank'
        
        if search_type == 'ifsc':
            # Search by IFSC code
            matches = self.data[self.data['IFSC'].str.upper().str.contains(query, na=False)]
            results = matches.to_dict('records')
            
        elif search_type == 'micr':
            # Search by MICR code
            matches = self.data[self.data['MICR'].str.contains(query, na=False)]
            results = matches.to_dict('records')
            
        elif search_type == 'bank':
            # Search by bank name, city, or branch
            mask = (
                self.data['Bank Name'].str.upper().str.contains(query, na=False) |
                self.data['City'].str.upper().str.contains(query, na=False) |
                self.data['Branch'].str.upper().str.contains(query, na=False)
            )
            matches = self.data[mask]
            results = matches.to_dict('records')
        
        return results[:50]  # Limit results for performance
    
    def get_by_ifsc(self, ifsc_code):
        """Get bank information by IFSC code"""
        if self.data is None or len(self.data) == 0:
            return None
        
        matches = self.data[self.data['IFSC'].str.upper() == ifsc_code.upper()]
        
        if len(matches) > 0:
            return matches.iloc[0].to_dict()
        return None
    
    def get_by_bank_city_branch(self, bank_slug, city, branch):
        """Get bank information by bank slug, city, and branch"""
        if self.data is None or len(self.data) == 0:
            return None
        
        # Convert slugs back to original format for matching
        city_original = city.replace('-', ' ').title()
        branch_original = branch.replace('-', ' ').title()
        
        # Find matching records
        for _, row in self.data.iterrows():
            if (self.create_slug(row['Bank Name']) == bank_slug and
                self.create_slug(row['City']) == city.lower() and
                self.create_slug(row['Branch']) == branch.lower()):
                return row.to_dict()
        
        return None
    
    def get_suggestions(self, query):
        """Get autocomplete suggestions"""
        if self.data is None or len(self.data) == 0:
            return []
        
        query = query.upper()
        suggestions = []
        
        # IFSC suggestions
        ifsc_matches = self.data[self.data['IFSC'].str.upper().str.startswith(query)]
        for ifsc in ifsc_matches['IFSC'].head(5):
            suggestions.append({
                'value': ifsc,
                'label': f"{ifsc} - IFSC Code",
                'type': 'ifsc'
            })
        
        # Bank name suggestions
        bank_matches = self.data[self.data['Bank Name'].str.upper().str.contains(query, na=False)]
        for bank in bank_matches['Bank Name'].unique()[:5]:
            suggestions.append({
                'value': bank,
                'label': f"{bank} - Bank",
                'type': 'bank'
            })
        
        # City suggestions
        city_matches = self.data[self.data['City'].str.upper().str.contains(query, na=False)]
        for city in city_matches['City'].unique()[:3]:
            suggestions.append({
                'value': city,
                'label': f"{city} - City",
                'type': 'city'
            })
        
        return suggestions[:10]
    
    def generate_sitemap(self):
        """Generate XML sitemap for SEO"""
        if self.data is None or len(self.data) == 0:
            return """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>http://localhost:5000/</loc>
        <lastmod>{}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
</urlset>""".format(datetime.now().strftime('%Y-%m-%d'))
        
        sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>http://localhost:5000/</loc>
        <lastmod>{}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
""".format(datetime.now().strftime('%Y-%m-%d'))
        
        # Add IFSC pages
        for ifsc in self.data['IFSC'].unique():
            if ifsc:
                sitemap_xml += f"""    <url>
        <loc>http://localhost:5000/ifsc/{ifsc}</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
"""
        
        # Add bank/city/branch pages
        for _, row in self.data.iterrows():
            if row['Bank Name'] and row['City'] and row['Branch']:
                bank_slug = self.create_slug(row['Bank Name'])
                city_slug = self.create_slug(row['City'])
                branch_slug = self.create_slug(row['Branch'])
                
                sitemap_xml += f"""    <url>
        <loc>http://localhost:5000/bank/{quote(bank_slug)}/{quote(city_slug)}/{quote(branch_slug)}</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
"""
        
        sitemap_xml += "</urlset>"
        return sitemap_xml
    
    def get_all_banks(self):
        """Get all unique banks"""
        if self.data is None or len(self.data) == 0:
            return []
        return self.data['Bank Name'].unique().tolist()
    
    def get_cities_by_bank(self, bank_name):
        """Get cities for a specific bank"""
        if self.data is None or len(self.data) == 0:
            return []
        bank_data = self.data[self.data['Bank Name'] == bank_name]
        return bank_data['City'].unique().tolist()
    
    def get_branches_by_bank_city(self, bank_name, city):
        """Get branches for a specific bank and city"""
        if self.data is None or len(self.data) == 0:
            return []
        bank_city_data = self.data[
            (self.data['Bank Name'] == bank_name) & 
            (self.data['City'] == city)
        ]
        return bank_city_data[['Branch', 'IFSC']].to_dict('records')
