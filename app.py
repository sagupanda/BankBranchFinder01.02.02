import os
import logging
from flask import Flask, render_template, request, jsonify, url_for, redirect
from flask_caching import Cache
from werkzeug.middleware.proxy_fix import ProxyFix
from urllib.parse import quote
import pandas as pd
from data_loader import BankDataLoader
import re
import requests

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

def get_bank_details_from_razorpay(ifsc_code):
    """Get bank details from Razorpay IFSC API"""
    try:
        url = f"https://ifsc.razorpay.com/{ifsc_code.upper()}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'IFSC': data.get('IFSC', ''),
                'BANK': data.get('BANK', ''),
                'BRANCH': data.get('BRANCH', ''),
                'CITY1': data.get('DISTRICT', ''),
                'CITY2': data.get('CITY', ''),
                'STATE': data.get('STATE', ''),
                'ADDRESS': data.get('ADDRESS', ''),
                'PHONE': '',
                'STD CODE': '',
                'CONTACT': data.get('CONTACT', ''),
                'RTGS': data.get('RTGS', False),
                'SWIFT': data.get('SWIFT', ''),
                'MICR': data.get('MICR', '')
            }
        else:
            return None
    except Exception as e:
        logging.error(f"Error fetching from Razorpay API: {e}")
        return None

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
        
        # Filter by bank name
        filtered_df = df[df['BANK'].str.contains(bank, case=False, na=False)]
        
        # Apply additional filters
        if city:
            filtered_df = filtered_df[
                (filtered_df['CITY1'].str.contains(city, case=False, na=False)) |
                (filtered_df['CITY2'].str.contains(city, case=False, na=False))
            ]
        
        if state:
            filtered_df = filtered_df[filtered_df['STATE'].str.contains(state, case=False, na=False)]
        
        if branch:
            filtered_df = filtered_df[filtered_df['BRANCH'].str.contains(branch, case=False, na=False)]
        
        results = filtered_df.to_dict('records')
        
        return render_template('search_results.html', 
                             results=results[:100],  # Limit results
                             query=f"Bank: {bank}" + (f", City: {city}" if city else "") + (f", State: {state}" if state else "") + (f", Branch: {branch}" if branch else ""),
                             search_type='bank_details')
    
    # Regular search
    if not query:
        return render_template('search_results.html', results=[], query="", error="Please enter a search term")
    
    # Auto-detect search type
    if search_type == 'auto':
        if len(query) == 11 and query.isalnum():
            search_type = 'ifsc'
        elif query.isdigit():
            search_type = 'phone'
        else:
            search_type = 'general'
    
    results = []
    
    if search_type == 'ifsc':
        # For IFSC search, try exact match first
        if len(query) == 11 and query.isalnum():
            # Try Razorpay API first for exact IFSC
            bank_info = get_bank_details_from_razorpay(query)
            if bank_info:
                return redirect(url_for('ifsc_detail', ifsc_code=query.upper()))
        
        # Search by IFSC code in CSV data
        filtered_df = df[df['IFSC'].str.contains(query, case=False, na=False)]
        results = filtered_df.to_dict('records')
        
        # If exact match found in CSV, redirect to IFSC detail page
        exact_match = df[df['IFSC'] == query.upper()]
        if len(exact_match) == 1:
            return redirect(url_for('ifsc_detail', ifsc_code=query.upper()))
    
    elif search_type == 'phone':
        # Search by phone number
        filtered_df = df[df['PHONE'].astype(str).str.contains(query, na=False)]
        results = filtered_df.to_dict('records')
    
    else:
        # General search across multiple fields
        filtered_df = df[
            (df['BANK'].str.contains(query, case=False, na=False)) |
            (df['BRANCH'].str.contains(query, case=False, na=False)) |
            (df['CITY1'].str.contains(query, case=False, na=False)) |
            (df['CITY2'].str.contains(query, case=False, na=False)) |
            (df['STATE'].str.contains(query, case=False, na=False)) |
            (df['ADDRESS'].str.contains(query, case=False, na=False))
        ]
        results = filtered_df.to_dict('records')
    
    return render_template('search_results.html', 
                         results=results[:100],  # Limit results
                         query=query,
                         search_type=search_type)

@app.route('/ifsc/<ifsc_code>')
def ifsc_detail(ifsc_code):
    """Show detailed information for a specific IFSC code"""
    df = init_data()
    
    # Try to get bank details from Razorpay API first
    bank_info = get_bank_details_from_razorpay(ifsc_code)
    
    # If Razorpay API fails, try CSV data
    if not bank_info:
        bank_record = df[df['IFSC'] == ifsc_code.upper()]
        if not bank_record.empty:
            bank_info = bank_record.iloc[0].to_dict()
    
    # If still no data found
    if not bank_info:
        return render_template('ifsc_detail.html', 
                             ifsc_code=ifsc_code,
                             error="IFSC code not found")
    
    # Find related branches in the same city from CSV data
    related_branches = df[
        (df['BANK'].str.contains(bank_info['BANK'], case=False, na=False)) &
        (df['CITY1'].str.contains(bank_info['CITY1'], case=False, na=False)) &
        (df['IFSC'] != ifsc_code.upper())
    ].head(5)
    
    return render_template('ifsc_detail.html',
                         ifsc_code=ifsc_code,
                         bank_info=bank_info,
                         related_branches=related_branches.to_dict('records'))

@app.route('/bank/<bank_slug>/<city_slug>/<branch_slug>')
def bank_branch_detail(bank_slug, city_slug, branch_slug):
    """Show detailed information for a specific bank branch"""
    df = init_data()
    
    # Find matching branch
    for _, row in df.iterrows():
        if (slugify(row['BANK']) == bank_slug and 
            slugify(row['CITY1']) == city_slug and 
            slugify(row['BRANCH']) == branch_slug):
            
            bank_info = row.to_dict()
            
            # Find related branches
            related_branches = df[
                (df['BANK'] == bank_info['BANK']) &
                (df['CITY1'] == bank_info['CITY1']) &
                (df['IFSC'] != bank_info['IFSC'])
            ].head(5)
            
            return render_template('bank_branch.html',
                                 bank_info=bank_info,
                                 related_branches=related_branches.to_dict('records'))
    
    return render_template('bank_branch.html',
                         error="Branch not found")

@app.route('/api/autocomplete')
def autocomplete():
    """API endpoint for autocomplete suggestions"""
    df = init_data()
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify([])
    
    suggestions = []
    
    # IFSC suggestions
    ifsc_matches = df[df['IFSC'].str.startswith(query.upper(), na=False)]['IFSC'].unique()
    for ifsc in ifsc_matches[:5]:
        suggestions.append({
            'value': ifsc,
            'label': f"{ifsc} - IFSC Code",
            'type': 'ifsc'
        })
    
    # Bank suggestions
    bank_matches = df[df['BANK'].str.contains(query, case=False, na=False)]['BANK'].unique()
    for bank in bank_matches[:5]:
        suggestions.append({
            'value': bank,
            'label': f"{bank} - Bank",
            'type': 'bank'
        })
    
    # City suggestions
    city1_matches = df[df['CITY1'].str.contains(query, case=False, na=False)]['CITY1'].unique()
    city2_matches = df[df['CITY2'].str.contains(query, case=False, na=False)]['CITY2'].unique()
    
    all_cities = set(list(city1_matches) + list(city2_matches))
    for city in list(all_cities)[:3]:
        suggestions.append({
            'value': city,
            'label': f"{city} - City",
            'type': 'city'
        })
    
    # Branch suggestions
    branch_matches = df[df['BRANCH'].str.contains(query, case=False, na=False)]['BRANCH'].unique()
    for branch in branch_matches[:3]:
        suggestions.append({
            'value': branch,
            'label': f"{branch} - Branch",
            'type': 'branch'
        })
    
    return jsonify(suggestions[:15])

@app.route('/api/banks')
def get_banks():
    """Get list of all banks"""
    df = init_data()
    banks = sorted(df['BANK'].unique())
    return jsonify(banks)

@app.route('/api/cities')
def get_cities():
    """Get list of all cities"""
    df = init_data()
    cities = set()
    cities.update(df['CITY1'].unique())
    cities.update(df['CITY2'].unique())
    return jsonify(sorted(list(cities)))

@app.route('/api/states')
def get_states():
    """Get list of all states"""
    df = init_data()
    states = sorted(df['STATE'].unique())
    return jsonify(states)

@app.route('/sitemap.xml')
@cache.cached(timeout=3600)
def sitemap():
    """Generate sitemap"""
    df = init_data()
    
    sitemap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://bankbranchfinder.com/</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
'''
    
    # Add IFSC pages
    for ifsc in df['IFSC'].unique():
        sitemap_xml += f'''    <url>
        <loc>https://bankbranchfinder.com/ifsc/{ifsc}</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
'''
    
    # Add bank branch pages
    for _, row in df.iterrows():
        bank_slug = slugify(row['BANK'])
        city_slug = slugify(row['CITY1'])
        branch_slug = slugify(row['BRANCH'])
        
        sitemap_xml += f'''    <url>
        <loc>https://bankbranchfinder.com/bank/{bank_slug}/{city_slug}/{branch_slug}</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
'''
    
    sitemap_xml += '</urlset>'
    
    response = app.response_class(
        response=sitemap_xml,
        status=200,
        mimetype='application/xml'
    )
    return response

@app.route('/robots.txt')
def robots():
    """Generate robots.txt"""
    robots_txt = '''User-agent: *
Allow: /
Disallow: /api/

Sitemap: https://bankbranchfinder.com/sitemap.xml
'''
    
    response = app.response_class(
        response=robots_txt,
        status=200,
        mimetype='text/plain'
    )
    return response

@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('index.html', error="Internal server error"), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)