# KnowYourIFSC - India's Most Comprehensive Bank Branch Directory

## Overview

KnowYourIFSC is a Flask-based web application that provides comprehensive IFSC (Indian Financial System Code) lookup services for 170,000+ Indian bank branches. The application allows users to search for bank branches by bank name, city, state, branch name, or IFSC code, and provides detailed branch information including addresses and contact details.

## System Architecture

### Frontend Architecture
- **Framework**: Bootstrap 5 with responsive design
- **JavaScript**: Vanilla JavaScript for autocomplete functionality
- **Templates**: Jinja2 templating engine with a base template system
- **Styling**: Custom CSS with CSS variables for consistent theming
- **Icons**: Font Awesome for UI icons

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Structure**: Modular design with separate data loading component
- **Caching**: Flask-Caching with simple in-memory cache
- **Middleware**: ProxyFix for proper header handling behind proxies
- **Logging**: Python logging for debugging and monitoring

## Key Components

### 1. Application Core (`app.py`)
- Main Flask application with route definitions
- Session management and security configuration
- Caching implementation for performance optimization
- URL slug generation for SEO-friendly URLs

### 2. Data Management (`data_loader.py`)
- `BankDataLoader` class for CSV data processing
- Data cleaning and standardization functionality
- Duplicate removal and data validation
- Error handling for missing data files

### 3. Frontend Templates
- **Base Template**: Common layout and navigation structure
- **Index**: Homepage with search functionality
- **Search Results**: Paginated search results display
- **IFSC Detail**: Detailed branch information pages
- **Bank Branch**: Bank-specific branch listings

### 4. Static Assets
- **CSS**: Custom styling with CSS variables and responsive design
- **JavaScript**: Autocomplete functionality with debouncing and keyboard navigation

## Data Flow

1. **Data Loading**: CSV files containing bank data are loaded and processed during application startup
2. **User Search**: Users submit search queries through the web interface
3. **Data Processing**: Search queries are processed against the loaded dataset
4. **Results Display**: Matching results are formatted and displayed with proper pagination
5. **Caching**: Search results and processed data are cached for improved performance

## External Dependencies

### Python Packages
- **Flask**: Web framework and routing
- **pandas**: Data manipulation and CSV processing
- **Flask-Caching**: Caching layer for performance
- **Werkzeug**: WSGI utilities and middleware

### Frontend Libraries
- **Bootstrap 5**: CSS framework for responsive design
- **Font Awesome 6**: Icon library for UI elements

### Data Sources
- Bank IFSC data stored in CSV files (`allbankifsc1.csv`, `allbankifsc2.csv`)
- Data includes bank names, IFSC codes, branch details, addresses, and contact information

## Deployment Strategy

### Development Setup
- **Entry Point**: `main.py` for local development
- **Configuration**: Environment-based configuration with fallbacks
- **Debug Mode**: Enabled for development with detailed error logging

### Production Considerations
- **WSGI**: Application configured for WSGI deployment
- **Proxy Support**: ProxyFix middleware for reverse proxy deployments
- **Security**: Session secret management through environment variables
- **SEO**: Robots.txt and sitemap support for search engine optimization

### Performance Optimizations
- **Caching**: In-memory caching for frequently accessed data
- **Data Loading**: One-time data loading on application startup
- **Autocomplete**: Debounced search suggestions to reduce server load

## Changelog
```
Changelog:
- July 05, 2025. Initial setup
- July 05, 2025. Added dynamic search modes with toggle between IFSC search and bank details search
- July 05, 2025. Implemented cascading dropdown filters for bank, state, city, and branch selection
- July 05, 2025. Added dark/light mode theme toggle with localStorage persistence
- July 05, 2025. Updated color scheme to blue and white theme
- July 05, 2025. Enhanced search results to display branch codes and N/A for missing values
- July 05, 2025. Fixed autocomplete error handling and improved API endpoints
- July 07, 2025. Swapped city/district data display (CITY2 now shows as City, CITY1 as District)
- July 07, 2025. Rebranded to KnowYourIFSC with new logo and SEO-optimized tagline
- July 07, 2025. Removed all MICR code functionality (not available in dataset)
- July 07, 2025. Set Bank Details search as default landing mode instead of IFSC search
- July 08, 2025. Updated logos: IFSCBLU.png for white backgrounds, IFSCWHT.png for blue backgrounds
- July 08, 2025. Updated domain references to "ifscbanksearch"
- July 08, 2025. Completely removed MICR code card from "How to Search" section
- July 08, 2025. Updated layout to use 2-column grid for remaining search examples
```

## User Preferences
```
Preferred communication style: Simple, everyday language.
Color scheme: Blue and white theme preferred
Features: Dynamic dropdowns with cascading filters, dark/light mode toggle
Data display: Show N/A for missing values, display branch codes from IFSC
```