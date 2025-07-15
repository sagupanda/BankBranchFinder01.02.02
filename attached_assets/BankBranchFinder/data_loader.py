import pandas as pd
import logging
import os

class BankDataLoader:
    def __init__(self):
        self.data = None
    
    def load_data(self):
        """Load and combine bank data from CSV files"""
        try:
            # Load both CSV files
            df1 = pd.read_csv('attached_assets/allbankifsc1.csv')
            df2 = pd.read_csv('attached_assets/allbankifsc2.csv')
            
            # Combine dataframes
            combined_df = pd.concat([df1, df2], ignore_index=True)
            
            # Clean and standardize data
            combined_df = self._clean_data(combined_df)
            
            logging.info(f"Loaded {len(combined_df)} bank records")
            self.data = combined_df
            return combined_df
            
        except Exception as e:
            logging.error(f"Error loading bank data: {e}")
            # Return empty dataframe if files not found
            return pd.DataFrame(columns=['BANK', 'IFSC', 'BRANCH', 'ADDRESS', 'CITY1', 'CITY2', 'STATE', 'STD CODE', 'PHONE'])
    
    def _clean_data(self, df):
        """Clean and standardize the bank data"""
        # Remove duplicates based on IFSC
        df = df.drop_duplicates(subset=['IFSC'], keep='first')
        
        # Clean text fields
        text_columns = ['BANK', 'BRANCH', 'ADDRESS', 'CITY1', 'CITY2', 'STATE']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].replace('nan', '')
        
        # Ensure IFSC is uppercase
        df['IFSC'] = df['IFSC'].str.upper()
        
        # Fill missing values
        df = df.fillna('')
        
        return df
    
    def get_unique_banks(self):
        """Get list of unique banks"""
        if self.data is not None:
            return sorted(self.data['BANK'].unique())
        return []
    
    def get_unique_cities(self):
        """Get list of unique cities"""
        if self.data is not None:
            cities = set()
            cities.update(self.data['CITY1'].unique())
            cities.update(self.data['CITY2'].unique())
            return sorted(list(cities))
        return []
    
    def search_by_ifsc(self, ifsc_code):
        """Search for branch by IFSC code"""
        if self.data is not None:
            result = self.data[self.data['IFSC'] == ifsc_code.upper()]
            return result.to_dict('records')
        return []
    
    def search_by_bank_city(self, bank_name, city_name):
        """Search branches by bank and city"""
        if self.data is not None:
            mask = (
                self.data['BANK'].str.contains(bank_name, case=False, na=False) &
                (self.data['CITY1'].str.contains(city_name, case=False, na=False) |
                 self.data['CITY2'].str.contains(city_name, case=False, na=False))
            )
            return self.data[mask].to_dict('records')
        return []
