# IFSC Code Finder - Flask Web Application

## Overview

This is a Flask web application that provides IFSC code lookup functionality for Indian banks. The application allows users to search for bank information using IFSC codes, bank names, cities, or branch names. It processes data from 170,671+ bank records stored in CSV files and provides a user-friendly interface for searching and displaying bank branch details.

## User Preferences

Preferred communication style: Simple, everyday language.
- Use Razorpay IFSC API for bank details search
- Use CSV files for IFSC code search and general bank searches
- Remove duplicate "KnowYourIFSC" branding

## Recent Changes (July 15, 2025)

✓ Integrated Razorpay IFSC API for accurate bank details lookup
✓ Fixed autocomplete JavaScript functionality 
✓ Removed duplicate branding text from templates
✓ Updated data loading to use CSV files (bank_data_1.csv, bank_data_2.csv)
✓ Fixed template variables from 'branch' to 'bank_info'
✓ Successfully tested IFSC search and autocomplete functionality
✓ Added N/A fallback for phone numbers and STD codes when unavailable
✓ Implemented dynamic bank details form with keyboard input and autocomplete
✓ Created contextual autocomplete API endpoints for banks, states, cities, and branches
✓ Added white IFSC logo on blue navbar background
✓ Fully separated data sources: Razorpay API for bank details, CSV for IFSC search

## System Architecture

### Frontend Architecture
- **Framework**: HTML templates with Jinja2 templating engine
- **UI Library**: Bootstrap 5.3.0 for responsive design and components
- **Icons**: Font Awesome 6.0.0 for iconography
- **JavaScript**: Vanilla JavaScript for interactive features including autocomplete functionality
- **CSS**: Custom CSS with CSS variables for theming, built on top of Bootstrap

### Backend Architecture
- **Framework**: Flask web framework
- **Data Processing**: Pandas for Excel file processing and data manipulation
- **Caching**: Flask-Caching with simple cache configuration
- **Logging**: Python's built-in logging module for debugging and monitoring
- **URL Routing**: Flask's URL routing with SEO-friendly slug generation

### Data Storage
- **Primary Data Source**: Excel file (`bank_data.xlsx`) containing bank information
- **Data Structure**: Columns include Bank Name, City, Branch, IFSC, MICR, Address, and State
- **In-Memory Processing**: Data is loaded into Pandas DataFrame for fast searching
- **No Database**: Currently uses file-based storage without a traditional database

## Key Components

### 1. Application Entry Point (`app.py`)
- Flask application initialization with secret key configuration
- Route definitions for homepage, search, and detail pages
- Integration with data processor for search functionality
- Caching implementation for performance optimization

### 2. Data Processing Layer (`data_processor.py`)
- `BankDataProcessor` class handles all data operations
- Excel file loading and data cleaning
- Search functionality with auto-detection of search types
- URL slug generation for SEO-friendly URLs

### 3. Template System
- **Base Template**: Common layout with navigation and Bootstrap integration
- **Index Template**: Homepage with search form and examples
- **Search Results Template**: Displays search results in card format
- **Detail Templates**: Individual pages for IFSC and bank branch details

### 4. Frontend Assets
- **JavaScript**: Autocomplete functionality with debouncing and keyboard navigation
- **CSS**: Custom styling with CSS variables and responsive design
- **Bootstrap Integration**: Utilizes Bootstrap's grid system and components

## Data Flow

1. **User Input**: User enters search query through the main search form
2. **Query Processing**: Flask routes handle the request and pass it to the data processor
3. **Data Search**: BankDataProcessor searches the loaded DataFrame based on query type
4. **Result Processing**: Results are formatted and passed to appropriate templates
5. **Template Rendering**: Jinja2 templates render the final HTML with search results
6. **Response Delivery**: Flask serves the rendered HTML to the user's browser

### Search Types
- **Auto-detection**: Automatically determines if input is IFSC, MICR, or general search
- **IFSC Search**: Direct lookup for 11-character alphanumeric codes
- **General Search**: Searches across bank names, cities, and branches
- **Single Result Handling**: Automatic redirection to detail pages for single IFSC results

## External Dependencies

### Python Libraries
- **Flask**: Web framework and routing
- **Pandas**: Data processing and Excel file handling
- **Flask-Caching**: Performance optimization through caching
- **urllib.parse**: URL encoding and decoding utilities

### Frontend Libraries
- **Bootstrap 5.3.0**: UI framework and responsive design
- **Font Awesome 6.0.0**: Icon library
- **CDN Delivery**: External libraries loaded via CDN for faster loading

### Data Dependencies
- **Excel File**: `bank_data.xlsx` containing bank information
- **File Format**: Must contain specific columns for proper data processing

## Deployment Strategy

### Development Setup
- **Entry Point**: `main.py` runs the Flask application in debug mode
- **Host Configuration**: Configured to run on `0.0.0.0:5000` for development
- **Debug Mode**: Enabled for development with detailed error reporting

### Production Considerations
- **Secret Key**: Uses environment variable `SESSION_SECRET` with fallback
- **Error Handling**: Comprehensive error handling for missing data files
- **Logging**: Configurable logging system for monitoring and debugging
- **Caching**: Simple caching implementation that can be upgraded for production

### SEO Optimization
- **URL Structure**: SEO-friendly URLs with slugs for bank and branch pages
- **Meta Tags**: Comprehensive meta tags including OpenGraph support
- **Canonical URLs**: Proper canonical URL implementation
- **Structured Navigation**: Breadcrumb navigation for better user experience

### Performance Features
- **Autocomplete**: Debounced search suggestions for better user experience
- **Caching**: Flask-Caching implementation for frequently accessed data
- **Responsive Design**: Mobile-first design approach with Bootstrap
- **CDN Integration**: External libraries loaded via CDN for faster loading