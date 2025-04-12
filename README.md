# Fruit Import/Export Analysis Dashboard

An interactive dashboard for analyzing fruit import/export data using Streamlit and Plotly.

## Features

- Interactive filters for transport mode, date range, varieties and more
- Multiple analysis pages:
  - Overview
  - Transport Analysis
  - Importer/Exporter Analysis
  - Port Analysis
  - Timeline Analysis
- Downloadable filtered data
- Interactive visualizations

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the app:
   ```
   streamlit run app.py
   ```

## Deployment

### Local Network Sharing

To share the app on your local network:

```bash
streamlit run app.py --server.address=0.0.0.0
```

Other users can access it using your computer's IP address (example: http://192.168.1.225:8501)

### Streamlit Cloud Deployment

1. Push your code to GitHub
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Connect your GitHub account
4. Deploy the app by selecting your repository

## Data Structure

The app expects a CSV file with the following columns:
- Season
- ETD Week
- ETA Week
- ETA
- Transport
- Specie
- Variety
- Importer
- Exporter
- Arrival port
- Vessel
- Boxes 