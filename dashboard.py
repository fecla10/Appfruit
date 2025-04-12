import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
from datetime import datetime
import os
import sys

def check_dependencies():
    required_packages = ['pandas', 'plotly', 'dash', 'dash-bootstrap-components']
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    return missing_packages

def find_csv_file():
    # List all files in the current directory
    files = os.listdir()
    # Look for files that contain 'tuesday' and end with '.csv'
    csv_files = [f for f in files if 'tuesday' in f.lower() and f.endswith('.csv')]
    if not csv_files:
        return None
    return csv_files[0]  # Return the first matching file

def main():
    print("Starting dashboard setup...")
    
    # Check dependencies
    missing_packages = check_dependencies()
    if missing_packages:
        print(f"\nMissing required packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return
    
    try:
        # Find the CSV file
        csv_file = find_csv_file()
        if not csv_file:
            raise FileNotFoundError("No CSV file found in the current directory")
        
        print(f"Found CSV file: {csv_file}")
        print(f"Reading CSV file from: {os.path.abspath(csv_file)}")
        
        # Load and preprocess data
        df = pd.read_csv(csv_file)
        print("CSV file loaded successfully")
        print(f"Number of rows in dataset: {len(df)}")
        
        # Convert date columns to datetime
        df['ETA'] = pd.to_datetime(df['ETA'], format='%d-%m-%Y')
        print("Date conversion completed")
        
        # Create week number column
        df['Week_Number'] = df['ETA'].dt.isocalendar().week
        print("Week number calculation completed")
        
        # Initialize the Dash app
        print("Initializing Dash app...")
        app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        
        # Define the layout
        app.layout = dbc.Container([
            dbc.Row([
                dbc.Col(html.H1("Fruit Import/Export Analysis Dashboard", className="text-center my-4"), width=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    html.H4("Transport Mode Distribution"),
                    dcc.Graph(id='transport-pie')
                ], width=6),
                dbc.Col([
                    html.H4("Top Importers by Volume"),
                    dcc.Graph(id='importer-bar')
                ], width=6)
            ]),
            
            dbc.Row([
                dbc.Col([
                    html.H4("Weekly Shipment Volume"),
                    dcc.Graph(id='weekly-volume')
                ], width=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    html.H4("Port Distribution"),
                    dcc.Graph(id='port-pie')
                ], width=6),
                dbc.Col([
                    html.H4("Variety Distribution"),
                    dcc.Graph(id='variety-pie')
                ], width=6)
            ]),
            
            dbc.Row([
                dbc.Col([
                    html.H4("Shipment Volume by Transport Mode Over Time"),
                    dcc.Graph(id='transport-trend')
                ], width=12)
            ])
        ])
        
        # Callbacks for interactive visualizations
        @app.callback(
            Output('transport-pie', 'figure'),
            Input('transport-pie', 'id')
        )
        def update_transport_pie(_):
            transport_counts = df['Transport'].value_counts()
            fig = px.pie(values=transport_counts.values, names=transport_counts.index, 
                         title='Distribution of Transport Modes')
            return fig
        
        @app.callback(
            Output('importer-bar', 'figure'),
            Input('importer-bar', 'id')
        )
        def update_importer_bar(_):
            importer_volume = df.groupby('Importer')['Boxes'].sum().sort_values(ascending=False).head(10)
            fig = px.bar(x=importer_volume.index, y=importer_volume.values,
                         title='Top 10 Importers by Volume')
            fig.update_layout(xaxis_title="Importer", yaxis_title="Total Boxes")
            return fig
        
        @app.callback(
            Output('weekly-volume', 'figure'),
            Input('weekly-volume', 'id')
        )
        def update_weekly_volume(_):
            weekly_data = df.groupby('Week_Number')['Boxes'].sum().reset_index()
            fig = px.line(weekly_data, x='Week_Number', y='Boxes',
                          title='Weekly Shipment Volume')
            fig.update_layout(xaxis_title="Week Number", yaxis_title="Total Boxes")
            return fig
        
        @app.callback(
            Output('port-pie', 'figure'),
            Input('port-pie', 'id')
        )
        def update_port_pie(_):
            port_counts = df['Arrival port'].value_counts()
            fig = px.pie(values=port_counts.values, names=port_counts.index,
                         title='Distribution of Arrival Ports')
            return fig
        
        @app.callback(
            Output('variety-pie', 'figure'),
            Input('variety-pie', 'id')
        )
        def update_variety_pie(_):
            variety_counts = df['Variety'].value_counts()
            fig = px.pie(values=variety_counts.values, names=variety_counts.index,
                         title='Distribution of Fruit Varieties')
            return fig
        
        @app.callback(
            Output('transport-trend', 'figure'),
            Input('transport-trend', 'id')
        )
        def update_transport_trend(_):
            transport_weekly = df.groupby(['Week_Number', 'Transport'])['Boxes'].sum().reset_index()
            fig = px.line(transport_weekly, x='Week_Number', y='Boxes', color='Transport',
                          title='Shipment Volume by Transport Mode Over Time')
            fig.update_layout(xaxis_title="Week Number", yaxis_title="Total Boxes")
            return fig
        
        print("\nStarting server...")
        print("Please wait while the dashboard loads...")
        print("Once ready, you can access the dashboard at: http://127.0.0.1:8050/")
        app.run_server(debug=True, host='127.0.0.1', port=8050)

    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        print("\nPlease make sure:")
        print("1. All required packages are installed (run: pip install -r requirements.txt)")
        print("2. The CSV file is in the same directory as this script")
        print("3. No other application is using port 8050")
        print("4. You have the correct permissions to read the CSV file")
        print("\nCurrent working directory:", os.getcwd())
        print("Files in current directory:", os.listdir())

if __name__ == '__main__':
    main() 