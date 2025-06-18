# SPCA Maps

A Streamlit web application for visualizing food pantry locations and SPCA client density in Erie County, NY.

## Features

- Interactive map visualization of food pantry locations
- SPCA client density heatmap
- Data integration with Google Drive
- Geocoding capabilities for address data

## Setup

### Prerequisites

- Python 3.9.6 (recommended) or Python 3.9+
- Git

### Quick Setup

#### On macOS/Linux:
```bash
# Clone the repository
git clone <repository-url>
cd SPCA_Maps

# Run the setup script
./setup_venv.sh

# Activate the virtual environment
source venv/bin/activate

# Run the application
streamlit run app.py
```

#### On Windows:
```bash
# Clone the repository
git clone <repository-url>
cd SPCA_Maps

# Run the setup script
setup_venv.bat

# Activate the virtual environment
venv\Scripts\activate.bat

# Run the application
streamlit run app.py
```

### Manual Setup

If you prefer to set up manually:

1. Create a virtual environment:
   ```bash
   python3.9 -m venv venv
   ```

2. Activate the virtual environment:
   - macOS/Linux: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate.bat`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Environment Details

This application is configured to work with:
- Python 3.9.6
- Exact package versions specified in `requirements.txt`
- Virtual environment isolation

## Deployment

### Streamlit Cloud

The application is configured for deployment on Streamlit Cloud with:
- `runtime.txt` specifying Python 3.9.6
- `requirements.txt` with exact package versions
- Optimized for the Streamlit Cloud environment

### Local Development

For local development, use the virtual environment setup scripts to ensure consistency across different machines.

## Troubleshooting

### Common Issues

1. **Map not displaying**: Ensure all data files are present in the `map_data/` directory
2. **Package conflicts**: Use the exact versions specified in `requirements.txt`
3. **Python version issues**: Ensure you're using Python 3.9.6 or compatible version

### Environment Consistency

If the app works on one machine but not another:
1. Use the provided setup scripts to create identical environments
2. Ensure Python 3.9.6 is installed
3. Use the exact package versions from `requirements.txt`

## Development

This is a work in progress. The application is actively being developed and improved. 