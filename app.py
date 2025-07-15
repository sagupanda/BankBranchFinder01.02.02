import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_caching import Cache
from urllib.parse import quote, unquote
import re
from data_processor import BankDataProcessor

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")

# Configure caching
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Initialize data processor
data_processor = BankDataProcessor()

def create_slug(text):
    """Create URL-friendly slug from text"""
    if not text:
        return ""
    # Convert to lowercase and replace spaces/special chars with hyphens
    slug = re.sub(r'[^a-zA-Z0-9\s]', '', str(text).lower())
    slug = re.sub(r'\s+', '-', slug)
    return slug.strip('-')

@app.route('/')
def index():
    """Homepage with search functionality"""
    return render_template('index.html')

@app.route('/search')
def search():
    """Handle search requests"""
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'auto')
    
    if not query:
        return render_template('search_results.html', results=[], query=query, message="Please enter a search term")
    
    results = data_processor.search(query, search_type)
    
    # If single IFSC result, redirect to detail page
    if len(results) == 1 and search_type == 'ifsc':
        return redirect(url_for('ifsc_detail', ifsc_code=results[0]['IFSC']))
    
    return render_template('search_results.html', results=results, query=query)

@app.route('/ifsc/<ifsc_code>')
def ifsc_detail(ifsc_code):
    """Display detailed information for a specific IFSC code"""
    ifsc_code = ifsc_code.upper()
    bank_info = data_processor.get_by_ifsc(ifsc_code)
    
    if not bank_info:
        return render_template('ifsc_detail.html', error="IFSC code not found", ifsc_code=ifsc_code), 404
    
    return render_template('ifsc_detail.html', bank_info=bank_info, ifsc_code=ifsc_code)

@app.route('/bank/<bank_slug>/<city>/<branch>')
def bank_branch_detail(bank_slug, city, branch):
    """Display detailed information for a specific bank branch"""
    bank_slug = unquote(bank_slug)
    city = unquote(city)
    branch = unquote(branch)
    
    bank_info = data_processor.get_by_bank_city_branch(bank_slug, city, branch)
    
    if not bank_info:
        return render_template('bank_branch.html', error="Bank branch not found", 
                             bank_slug=bank_slug, city=city, branch=branch), 404
    
    return render_template('bank_branch.html', bank_info=bank_info, 
                         bank_slug=bank_slug, city=city, branch=branch)

@app.route('/autocomplete')
def autocomplete():
    """Provide autocomplete suggestions for search"""
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify([])
    
    suggestions = data_processor.get_suggestions(query)
    return jsonify(suggestions)

@app.route('/sitemap.xml')
@cache.cached(timeout=3600)  # Cache for 1 hour
def sitemap():
    """Generate sitemap for SEO"""
    sitemap_xml = data_processor.generate_sitemap()
    response = app.make_response(sitemap_xml)
    response.headers['Content-Type'] = 'application/xml'
    return response

@app.route('/robots.txt')
def robots_txt():
    """Generate robots.txt for search engines"""
    robots_content = """User-agent: *
Allow: /
Disallow: /autocomplete

Sitemap: {}/sitemap.xml
""".format(request.url_root.rstrip('/'))
    
    response = app.make_response(robots_content)
    response.headers['Content-Type'] = 'text/plain'
    return response

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('index.html', error="Internal server error"), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
