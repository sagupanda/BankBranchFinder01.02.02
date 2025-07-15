import os
import logging
from flask import Flask, render_template, request, jsonify, url_for
from flask_caching import Cache
from werkzeug.middleware.proxy_fix import ProxyFix
from urllib.parse import quote
import pandas as pd
from data_loader import BankDataLoader
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure caching
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Initialize data loader
data_loader = BankDataLoader()
bank_data = None

def init_data():
    global bank_data
    if bank_data is None:
        bank_data = data_loader.load_data()
    return bank_data

def slugify(text):
    """Convert text to URL-friendly slug"""
    text = str(text).lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

# Initialize data when app starts
with app.app_context():
    init_data()

@app.route('/')
def index():
    """Homepage with search functionality"""
    df = init_data()
    
    # Get sample data for examples
    sample_ifsc = df['IFSC'].iloc[0] if not df.empty else "SBIN0000001"
    sample_bank = df['BANK'].iloc[0] if not df.empty else "STATE BANK OF INDIA"
    sample_city = df['CITY1'].iloc[0] if not df.empty else "MUMBAI"
    
    return render_template('index.html', 
                         sample_ifsc=sample_ifsc,
                         sample_bank=sample_bank,
                         sample_city=sample_city,
                         total_banks=len(df['BANK'].unique()),
                         total_branches=len(df))

@app.route('/search')
def search():
    """Search functionality"""
    df = init_data()
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'auto')
    
    # Handle bank details search
    if search_type == 'bank_details':
        bank = request.args.get('bank', '').strip()
        city = request.args.get('city', '').strip()
        state = request.args.get('state', '').strip()
        branch = request.args.get('branch', '').strip()
        
        if not bank:
            return render_template('search_results.html', results=[], query="", error="Please enter at least a bank name")
        
        try:
            # Build search mask for bank details
            mask = df['BANK'].str.contains(bank, case=False, na=False)
            
            if city:
                # CITY2 is now the main city, CITY1 is district
                city_mask = (
                    df['CITY2'].str.contains(city, case=False, na=False) |
                    df['CITY1'].str.contains(city, case=False, na=False)
                )
                mask = mask & city_mask
            
            if state:
                mask = mask & df['STATE'].str.contains(state, case=False, na=False)
            
            if branch:
                mask = mask & df['BRANCH'].str.contains(branch, case=False, na=False)
            
            results = df[mask].head(50).to_dict('records')
            search_query = f"{bank}"
            if city: search_query += f" in {city}"
            if state: search_query += f", {state}"
            if branch: search_query += f" - {branch}"
            
            return render_template('search_results.html', results=results, query=search_query)
            
        except Exception as e:
            logging.error(f"Bank details search error: {e}")
            return render_template('search_results.html', results=[], query="", error="Search error occurred")
    
    # Regular search functionality
    if not query:
        return render_template('search_results.html', results=[], query=query, error="Please enter a search term")
    
    results = []
    
    try:
        if search_type == 'ifsc' or (search_type == 'auto' and len(query) == 11 and query.isalnum()):
            # Search by IFSC
            results = df[df['IFSC'].str.upper() == query.upper()].to_dict('records')
        elif search_type == 'micr' or (search_type == 'auto' and query.isdigit() and len(query) == 9):
            # Search by MICR (if column exists)
            if 'MICR' in df.columns:
                results = df[df['MICR'].astype(str) == query].to_dict('records')
            else:
                # MICR data not available, return empty results with helpful message
                return render_template('search_results.html', 
                                     results=[], 
                                     query=query, 
                                     error="MICR code search is not available. Our database doesn't include MICR codes. Please try searching by IFSC code, bank name, or city instead.")
        else:
            # Search by bank name, city, or branch
            # CITY2 is now the main city, CITY1 is district
            mask = (
                df['BANK'].str.contains(query, case=False, na=False) |
                df['CITY2'].str.contains(query, case=False, na=False) |
                df['CITY1'].str.contains(query, case=False, na=False) |
                df['BRANCH'].str.contains(query, case=False, na=False) |
                df['STATE'].str.contains(query, case=False, na=False)
            )
            results = df[mask].head(50).to_dict('records')  # Limit to 50 results
            
    except Exception as e:
        logging.error(f"Search error: {e}")
        return render_template('search_results.html', results=[], query=query, error="Search error occurred")
    
    return render_template('search_results.html', results=results, query=query)

@app.route('/ifsc/<ifsc_code>')
def ifsc_detail(ifsc_code):
    """Individual IFSC detail page"""
    df = init_data()
    
    result = df[df['IFSC'].str.upper() == ifsc_code.upper()]
    
    if result.empty:
        return render_template('ifsc_detail.html', ifsc_code=ifsc_code, branch=None, error="IFSC code not found")
    
    branch = result.iloc[0].to_dict()
    
    # Get related branches from same bank and city
    related_branches = df[
        (df['BANK'] == branch['BANK']) & 
        (df['CITY1'] == branch['CITY1']) & 
        (df['IFSC'] != branch['IFSC'])
    ].head(10).to_dict('records')
    
    return render_template('ifsc_detail.html', 
                         ifsc_code=ifsc_code, 
                         branch=branch, 
                         related_branches=related_branches)

@app.route('/bank/<bank_slug>/<city>/<branch>')
def bank_branch_detail(bank_slug, city, branch):
    """Bank branch detail page"""
    df = init_data()
    
    # Try to find matching bank and branch
    # Convert slugs back to readable format for matching
    city_decoded = city.replace('-', ' ').title()
    branch_decoded = branch.replace('-', ' ').title()
    
    # Search for matching records
    mask = (
        df['CITY1'].str.contains(city_decoded, case=False, na=False) &
        df['BRANCH'].str.contains(branch_decoded, case=False, na=False)
    )
    
    results = df[mask]
    
    if results.empty:
        return render_template('bank_branch.html', 
                             bank_slug=bank_slug, 
                             city=city, 
                             branch=branch,
                             branches=[], 
                             error="Branch not found")
    
    branches = results.to_dict('records')
    bank_name = branches[0]['BANK'] if branches else ""
    
    return render_template('bank_branch.html', 
                         bank_slug=bank_slug,
                         city=city,
                         branch=branch,
                         bank_name=bank_name,
                         branches=branches)

@app.route('/api/autocomplete')
def autocomplete():
    """Autocomplete API for search suggestions"""
    try:
        df = init_data()
        query = request.args.get('q', '').strip().lower()
        
        if len(query) < 2:
            return jsonify([])
        
        suggestions = set()
        
        # Add bank names
        try:
            banks = df['BANK'].str.lower().str.contains(query, na=False)
            bank_matches = df[banks]['BANK'].dropna().unique()
            suggestions.update(bank_matches[:10].tolist())
        except Exception as e:
            logging.error(f"Bank autocomplete error: {e}")
        
        # Add cities (CITY2 is now the main city)
        try:
            cities2 = df['CITY2'].str.lower().str.contains(query, na=False)
            city2_matches = df[cities2]['CITY2'].dropna().unique()
            suggestions.update(city2_matches[:10].tolist())
            
            # Also add districts (CITY1)
            cities1 = df['CITY1'].str.lower().str.contains(query, na=False)
            city1_matches = df[cities1]['CITY1'].dropna().unique()
            suggestions.update(city1_matches[:5].tolist())
        except Exception as e:
            logging.error(f"City autocomplete error: {e}")
        
        # Add IFSC codes
        try:
            if query.isalnum():
                ifsc_matches = df['IFSC'].str.lower().str.contains(query, na=False)
                ifsc_codes = df[ifsc_matches]['IFSC'].dropna().unique()
                suggestions.update(ifsc_codes[:5].tolist())
        except Exception as e:
            logging.error(f"IFSC autocomplete error: {e}")
        
        return jsonify(list(suggestions)[:15])
    except Exception as e:
        logging.error(f"Autocomplete error: {e}")
        return jsonify([])

@app.route('/api/banks')
def get_banks():
    """Get all unique bank names"""
    try:
        df = init_data()
        banks = sorted(df['BANK'].dropna().unique().tolist())
        return jsonify(banks)
    except Exception as e:
        logging.error(f"Error fetching banks: {e}")
        return jsonify([])

@app.route('/api/states')
def get_states():
    """Get states filtered by bank"""
    try:
        df = init_data()
        bank = request.args.get('bank', '').strip()
        
        if bank:
            filtered_df = df[df['BANK'] == bank]
        else:
            filtered_df = df
            
        states = sorted(filtered_df['STATE'].dropna().unique().tolist())
        return jsonify(states)
    except Exception as e:
        logging.error(f"Error fetching states: {e}")
        return jsonify([])

@app.route('/api/cities')
def get_cities():
    """Get cities filtered by bank and state"""
    try:
        df = init_data()
        bank = request.args.get('bank', '').strip()
        state = request.args.get('state', '').strip()
        
        filtered_df = df
        if bank:
            filtered_df = filtered_df[filtered_df['BANK'] == bank]
        if state:
            filtered_df = filtered_df[filtered_df['STATE'] == state]
            
        cities = set()
        # CITY2 is now treated as the main city, CITY1 as district
        cities.update(filtered_df['CITY2'].dropna().unique().tolist())
        cities.update(filtered_df['CITY1'].dropna().unique().tolist())
        cities = sorted(list(cities))
        
        return jsonify(cities)
    except Exception as e:
        logging.error(f"Error fetching cities: {e}")
        return jsonify([])

@app.route('/api/branches')
def get_branches():
    """Get branches filtered by bank, state, and city"""
    try:
        df = init_data()
        bank = request.args.get('bank', '').strip()
        state = request.args.get('state', '').strip()
        city = request.args.get('city', '').strip()
        
        filtered_df = df
        if bank:
            filtered_df = filtered_df[filtered_df['BANK'] == bank]
        if state:
            filtered_df = filtered_df[filtered_df['STATE'] == state]
        if city:
            # CITY2 is now the main city, CITY1 is district
            city_mask = (
                filtered_df['CITY2'] == city
            ) | (
                filtered_df['CITY1'] == city
            )
            filtered_df = filtered_df[city_mask]
            
        branches = sorted(filtered_df['BRANCH'].dropna().unique().tolist())
        return jsonify(branches)
    except Exception as e:
        logging.error(f"Error fetching branches: {e}")
        return jsonify([])

@app.route('/sitemap.xml')
def sitemap():
    """Generate sitemap for SEO"""
    df = init_data()
    
    # Generate URLs for all IFSC codes
    urls = []
    
    # Add main pages
    urls.append(url_for('index', _external=True))
    
    # Add IFSC pages (limit to prevent huge sitemap)
    for ifsc in df['IFSC'].unique()[:1000]:  # Limit to 1000 for performance
        urls.append(url_for('ifsc_detail', ifsc_code=ifsc, _external=True))
    
    # Add bank-city-branch pages (limited sample)
    for _, row in df.head(500).iterrows():
        bank_slug = slugify(row['BANK'])
        city_slug = slugify(row['CITY1'])
        branch_slug = slugify(row['BRANCH'])
        urls.append(url_for('bank_branch_detail', 
                           bank_slug=bank_slug,
                           city=city_slug,
                           branch=branch_slug,
                           _external=True))
    
    response = app.response_class(
        render_template('sitemap.xml', urls=urls),
        mimetype='application/xml'
    )
    return response

@app.route('/robots.txt')
def robots():
    """Robots.txt for search engines"""
    response = app.response_class(
        render_template('robots.txt'),
        mimetype='text/plain'
    )
    return response

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('index.html', error="Server error occurred"), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
