import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime
import numpy as np

# Custom exception to catch and handle missing modules
class MissingDependencyError(Exception):
    pass

# Function to install missing dependencies
def install_missing_dependencies():
    st.warning("Installing required packages... This might take a moment.")
    
    try:
        # Try to install with pip
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly==5.13.1"])
        st.success("Packages installed successfully! Please refresh the page.")
        
        # Force a hard refresh by stopping the script
        st.stop()
    except Exception as e:
        st.error(f"Failed to install packages: {str(e)}")
        st.info("Please make sure the requirements.txt file contains 'plotly==5.13.1'")
        st.stop()

# Try to import plotly packages
try:
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:
    st.error("Unable to import plotly modules. Attempting to install...")
    install_missing_dependencies()

# Add debug information
print("Starting Streamlit app...")
print("Current working directory:", os.getcwd())
print("Python version:", sys.version)
print("Files in directory:", os.listdir())

# Set page config
st.set_page_config(
    page_title="Fruit Import/Export Analysis",
    page_icon="🍇",
    layout="wide"
)

# Apply custom CSS for better styling
st.markdown("""
<style>
    .main .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    .stMetric {background-color: #f7f7f7; padding: 15px; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);}
    .stMetric label {font-weight: bold; color: #31333F;}
    h1 {color: #2c3e50;}
    h2 {color: #34495e; padding-top: 1rem;}
    h3 {color: #7396b9;}
    .stSidebar {background-color: #f8f9fa;}
    .stSidebar .block-container {padding-top: 2rem;}
</style>
""", unsafe_allow_html=True)

# Title
st.title("🍇 Fruit Import/Export Analysis Dashboard")
st.markdown("Interactive dashboard for analyzing fruit import/export data")

# Function to find and load the CSV file
def load_data():
    try:
        print("Looking for CSV file...")
        files = os.listdir()
        print("Available files:", files)
        
        csv_files = [f for f in files if 'tuesday' in f.lower() and f.endswith('.csv')]
        print("Found CSV files:", csv_files)
        
        if not csv_files:
            st.error("No CSV file found in the current directory")
            return None
            
        csv_file = csv_files[0]
        print(f"Loading CSV file: {csv_file}")
        
        df = pd.read_csv(csv_file)
        print(f"Successfully loaded {len(df)} rows")
        
        # Data preprocessing
        df['ETA'] = pd.to_datetime(df['ETA'], format='%d-%m-%Y')
        df['ETD Week'] = df['ETD Week'].astype(str)
        df['ETA Week'] = df['ETA Week'].astype(str)
        df['Week_Number'] = df['ETA'].dt.isocalendar().week
        df['Month'] = df['ETA'].dt.month
        df['Month_Name'] = df['ETA'].dt.strftime('%B')
        df['Year'] = df['ETA'].dt.year
        
        # Calculate transit time (days between ETD week start and ETA)
        df['Transit_Days'] = df.apply(
            lambda row: calculate_transit_days(row['ETD Week'], row['ETA']), 
            axis=1
        )
        
        return df
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        st.error(f"Error loading data: {str(e)}")
        return None

def calculate_transit_days(etd_week, eta):
    try:
        # Extract year and week from ETD Week (e.g., "49-2023")
        if isinstance(etd_week, str) and '-' in etd_week:
            week, year = etd_week.split('-')
            # Approximate ETD date as the first day of the week
            from datetime import datetime, timedelta
            etd_date = datetime.strptime(f'{year}-W{week}-1', '%Y-W%W-%w')
            # Calculate days between ETD and ETA
            return (eta - etd_date).days
    except:
        pass
    return np.nan

# Load data
df = load_data()
if df is None:
    st.error("Failed to load data. Please check the console for more information.")
    st.stop()

# Sidebar - Dashboard Navigation
st.sidebar.title("Dashboard Navigation")
pages = ["Overview", "Transport Analysis", "Importer/Exporter Analysis", "Port Analysis", "Timeline Analysis"]
selected_page = st.sidebar.radio("Select Page", pages)

# Sidebar - Global Filters
st.sidebar.title("Global Filters")

# Filter explanations toggle
with st.sidebar.expander("ℹ️ Filter Info"):
    st.write("These filters apply to all dashboard sections.")
    st.write("You can select multiple options for each filter.")
    st.write("Use the date range picker to focus on specific time periods.")

# Season filter
seasons = df['Season'].unique()
selected_seasons = st.sidebar.multiselect(
    "Season",
    options=seasons,
    default=seasons
)

# Transport mode filter
transport_modes = df['Transport'].unique()
selected_transport = st.sidebar.multiselect(
    "Transport Mode",
    options=transport_modes,
    default=transport_modes
)

# Species filter
species = df['Specie'].unique()
selected_species = st.sidebar.multiselect(
    "Species",
    options=species,
    default=species
)

# Variety filter
varieties = df['Variety'].unique()
selected_varieties = st.sidebar.multiselect(
    "Variety",
    options=varieties,
    default=varieties
)

# Date range filter
min_date = df['ETA'].min().date()
max_date = df['ETA'].max().date()
date_range = st.sidebar.date_input(
    "Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Handle single date selection
if len(date_range) == 1:
    start_date = date_range[0]
    end_date = max_date
elif len(date_range) == 2:
    start_date = date_range[0]
    end_date = date_range[1]

# Apply filters
filtered_df = df[
    (df['Season'].isin(selected_seasons)) &
    (df['Transport'].isin(selected_transport)) &
    (df['Specie'].isin(selected_species)) &
    (df['Variety'].isin(selected_varieties)) &
    (df['ETA'].dt.date >= start_date) &
    (df['ETA'].dt.date <= end_date)
]

# Download button for filtered data
st.sidebar.download_button(
    label="Download Filtered Data",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name='filtered_fruit_data.csv',
    mime='text/csv',
)

# Display metrics based on the filtered dataframe
if selected_page == "Overview":
    st.header("📊 Dashboard Overview")
    
    # Key metrics in a row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Shipments", f"{len(filtered_df):,}")
    with col2:
        st.metric("Total Boxes", f"{filtered_df['Boxes'].sum():,}")
    with col3:
        st.metric("Unique Importers", filtered_df['Importer'].nunique())
    with col4:
        st.metric("Unique Exporters", filtered_df['Exporter'].nunique())
    
    # Second row of metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg Boxes per Shipment", f"{filtered_df['Boxes'].mean():.1f}")
    with col2:
        if 'Transit_Days' in filtered_df.columns:
            avg_transit = filtered_df['Transit_Days'].dropna().mean()
            st.metric("Avg Transit Days", f"{avg_transit:.1f}")
    with col3:
        st.metric("Unique Varieties", filtered_df['Variety'].nunique())
    with col4:
        st.metric("Unique Ports", filtered_df['Arrival port'].nunique())
    
    # Overview charts
    st.subheader("Transport & Import Distribution")
    col1, col2 = st.columns(2)
    
    with col1:
        transport_counts = filtered_df['Transport'].value_counts().reset_index()
        transport_counts.columns = ['Transport', 'Count']
        fig = px.pie(transport_counts, values='Count', names='Transport',
                    title='Distribution of Transport Modes',
                    color_discrete_sequence=px.colors.sequential.Viridis)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        importer_volume = filtered_df.groupby('Importer')['Boxes'].sum().sort_values(ascending=False).head(10).reset_index()
        fig = px.bar(importer_volume, x='Importer', y='Boxes',
                    title='Top 10 Importers by Volume',
                    color='Boxes', color_continuous_scale='Viridis')
        fig.update_layout(xaxis_title="Importer", yaxis_title="Total Boxes")
        st.plotly_chart(fig, use_container_width=True)
    
    # Weekly volume trend
    st.subheader("Shipment Volume Over Time")
    time_unit = st.radio("Time Aggregation", ["Weekly", "Monthly"], horizontal=True)
    
    if time_unit == "Weekly":
        time_data = filtered_df.groupby('Week_Number')['Boxes'].sum().reset_index()
        fig = px.line(time_data, x='Week_Number', y='Boxes',
                    title='Weekly Shipment Volume',
                    markers=True)
        fig.update_layout(xaxis_title="Week Number", yaxis_title="Total Boxes")
    else:
        time_data = filtered_df.groupby(['Year', 'Month', 'Month_Name'])['Boxes'].sum().reset_index()
        time_data = time_data.sort_values(['Year', 'Month'])
        fig = px.line(time_data, x='Month_Name', y='Boxes',
                    title='Monthly Shipment Volume',
                    markers=True)
        fig.update_layout(xaxis_title="Month", yaxis_title="Total Boxes")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Variety and port distribution
    st.subheader("Product & Destination Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        variety_counts = filtered_df['Variety'].value_counts().reset_index()
        variety_counts.columns = ['Variety', 'Count']
        fig = px.pie(variety_counts, values='Count', names='Variety',
                    title='Distribution of Fruit Varieties')
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        port_counts = filtered_df['Arrival port'].value_counts().reset_index()
        port_counts.columns = ['Port', 'Count']
        fig = px.pie(port_counts, values='Count', names='Port',
                    title='Distribution of Arrival Ports')
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    # Raw data view with expander
    with st.expander("View Raw Data"):
        st.dataframe(filtered_df)

elif selected_page == "Transport Analysis":
    st.header("🚢 Transport Analysis")
    
    # Transport metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Transport Modes", filtered_df['Transport'].nunique())
    with col2:
        top_transport = filtered_df.groupby('Transport')['Boxes'].sum().sort_values(ascending=False).index[0]
        st.metric("Most Common Transport", top_transport)
    with col3:
        top_transport_volume = filtered_df.groupby('Transport')['Boxes'].sum().sort_values(ascending=False).iloc[0]
        st.metric("Highest Volume (Boxes)", f"{top_transport_volume:,}")
    
    # Transport mode breakdown
    st.subheader("Transport Mode Analysis")
    
    # Transport mode comparison
    transport_volume = filtered_df.groupby('Transport')['Boxes'].sum().reset_index()
    transport_count = filtered_df.groupby('Transport').size().reset_index(name='Shipments')
    transport_data = pd.merge(transport_volume, transport_count, on='Transport')
    transport_data['Avg Boxes per Shipment'] = transport_data['Boxes'] / transport_data['Shipments']
    
    fig = px.bar(transport_data, x='Transport', y='Boxes',
                 title='Transport Mode Comparison',
                 color='Shipments', text='Shipments',
                 hover_data=['Avg Boxes per Shipment'])
    fig.update_layout(xaxis_title="Transport Mode", yaxis_title="Total Boxes")
    st.plotly_chart(fig, use_container_width=True)
    
    # Transport mode trends over time
    st.subheader("Transport Trends Over Time")
    
    # Group by month and transport
    transport_time = filtered_df.groupby(['Year', 'Month', 'Transport'])['Boxes'].sum().reset_index()
    transport_time['Date'] = pd.to_datetime(transport_time[['Year', 'Month']].assign(day=1))
    
    fig = px.line(transport_time, x='Date', y='Boxes', color='Transport',
                  title='Transport Volume Over Time',
                  markers=True)
    fig.update_layout(xaxis_title="Date", yaxis_title="Total Boxes")
    st.plotly_chart(fig, use_container_width=True)
    
    # Transport by destination port
    st.subheader("Transport by Destination")
    
    transport_port = filtered_df.groupby(['Transport', 'Arrival port'])['Boxes'].sum().reset_index()
    fig = px.sunburst(transport_port, path=['Transport', 'Arrival port'], values='Boxes',
                     title='Transport Modes by Destination Port')
    st.plotly_chart(fig, use_container_width=True)
    
    # Transit time analysis if available
    if 'Transit_Days' in filtered_df.columns:
        st.subheader("Transit Time Analysis")
        
        # Calculate average transit time by transport mode
        transit_by_transport = filtered_df.groupby('Transport')['Transit_Days'].mean().reset_index()
        transit_by_transport = transit_by_transport.sort_values('Transit_Days')
        
        fig = px.bar(transit_by_transport, x='Transport', y='Transit_Days',
                     title='Average Transit Time by Transport Mode',
                     color='Transit_Days')
        fig.update_layout(xaxis_title="Transport Mode", yaxis_title="Average Transit Days")
        st.plotly_chart(fig, use_container_width=True)
    
    # Vessel analysis for sea transport
    st.subheader("Vessel Analysis")
    sea_transport_df = filtered_df[filtered_df['Transport'].isin(['LINER', 'CHARTER'])]
    
    if not sea_transport_df.empty:
        vessel_volume = sea_transport_df.groupby('Vessel')['Boxes'].sum().sort_values(ascending=False).head(10).reset_index()
        
        fig = px.bar(vessel_volume, x='Vessel', y='Boxes',
                     title='Top 10 Vessels by Volume',
                     color='Boxes')
        fig.update_layout(xaxis_title="Vessel", yaxis_title="Total Boxes")
        st.plotly_chart(fig, use_container_width=True)

elif selected_page == "Importer/Exporter Analysis":
    st.header("🏢 Importer/Exporter Analysis")
    
    # Importer/Exporter metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Unique Importers", filtered_df['Importer'].nunique())
    with col2:
        st.metric("Unique Exporters", filtered_df['Exporter'].nunique())
    with col3:
        st.metric("Total Partnerships", filtered_df.groupby(['Importer', 'Exporter']).ngroups)
    
    # Top importers
    st.subheader("Top Importers Analysis")
    
    importer_volume = filtered_df.groupby('Importer')['Boxes'].sum().sort_values(ascending=False).head(10).reset_index()
    fig = px.bar(importer_volume, x='Importer', y='Boxes',
                 title='Top 10 Importers by Volume',
                 color='Boxes', color_continuous_scale='Viridis')
    fig.update_layout(xaxis_title="Importer", yaxis_title="Total Boxes")
    st.plotly_chart(fig, use_container_width=True)
    
    # Top exporters
    st.subheader("Top Exporters Analysis")
    
    exporter_volume = filtered_df.groupby('Exporter')['Boxes'].sum().sort_values(ascending=False).head(10).reset_index()
    fig = px.bar(exporter_volume, x='Exporter', y='Boxes',
                 title='Top 10 Exporters by Volume',
                 color='Boxes', color_continuous_scale='Viridis')
    fig.update_layout(xaxis_title="Exporter", yaxis_title="Total Boxes")
    st.plotly_chart(fig, use_container_width=True)
    
    # Importer-Exporter relationships
    st.subheader("Importer-Exporter Relationships")
    
    # Option to select specific importers/exporters for detailed analysis
    relationship_option = st.radio("Analyze relationships for:", ["Top Importers", "Top Exporters", "All"], horizontal=True)
    
    if relationship_option == "Top Importers":
        top_importers = filtered_df.groupby('Importer')['Boxes'].sum().sort_values(ascending=False).head(5).index
        relationship_df = filtered_df[filtered_df['Importer'].isin(top_importers)]
    elif relationship_option == "Top Exporters":
        top_exporters = filtered_df.groupby('Exporter')['Boxes'].sum().sort_values(ascending=False).head(5).index
        relationship_df = filtered_df[filtered_df['Exporter'].isin(top_exporters)]
    else:
        relationship_df = filtered_df
    
    # Network graph would be ideal here but using sunburst as alternative
    relationship_volume = relationship_df.groupby(['Importer', 'Exporter'])['Boxes'].sum().reset_index()
    
    if len(relationship_volume) > 0:
        fig = px.sunburst(relationship_volume, path=['Importer', 'Exporter'], values='Boxes',
                         title='Importer-Exporter Relationships')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data to visualize relationships with current filters.")
    
    # Product analysis by importer/exporter
    st.subheader("Product Analysis by Importer/Exporter")
    
    analysis_by = st.selectbox("Analyze by:", ["Importer", "Exporter"])
    
    variety_by_entity = filtered_df.groupby([analysis_by, 'Variety'])['Boxes'].sum().reset_index()
    # Get top 5 entities
    top_entities = filtered_df.groupby(analysis_by)['Boxes'].sum().sort_values(ascending=False).head(5).index
    variety_by_top_entity = variety_by_entity[variety_by_entity[analysis_by].isin(top_entities)]
    
    if len(variety_by_top_entity) > 0:
        fig = px.bar(variety_by_top_entity, x=analysis_by, y='Boxes', color='Variety',
                     title=f'Varieties Handled by Top 5 {analysis_by}s',
                     barmode='group')
        fig.update_layout(xaxis_title=analysis_by, yaxis_title="Total Boxes")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data to visualize with current filters.")

elif selected_page == "Port Analysis":
    st.header("🚢 Port Analysis")
    
    # Port metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Ports", filtered_df['Arrival port'].nunique())
    with col2:
        top_port = filtered_df.groupby('Arrival port')['Boxes'].sum().sort_values(ascending=False).index[0]
        st.metric("Busiest Port", top_port)
    with col3:
        top_port_volume = filtered_df.groupby('Arrival port')['Boxes'].sum().sort_values(ascending=False).iloc[0]
        st.metric("Highest Volume (Boxes)", f"{top_port_volume:,}")
    
    # Port volume analysis
    st.subheader("Port Volume Analysis")
    
    port_volume = filtered_df.groupby('Arrival port')['Boxes'].sum().sort_values(ascending=False).reset_index()
    fig = px.bar(port_volume, x='Arrival port', y='Boxes',
                 title='Ports by Volume',
                 color='Boxes', color_continuous_scale='Viridis')
    fig.update_layout(xaxis_title="Arrival Port", yaxis_title="Total Boxes")
    st.plotly_chart(fig, use_container_width=True)
    
    # Port trends over time
    st.subheader("Port Trends Over Time")
    
    time_period = st.radio("Time Period:", ["Monthly", "Weekly"], horizontal=True)
    
    if time_period == "Monthly":
        port_time = filtered_df.groupby(['Year', 'Month', 'Arrival port'])['Boxes'].sum().reset_index()
        port_time['Date'] = pd.to_datetime(port_time[['Year', 'Month']].assign(day=1))
        x_axis = 'Date'
        x_title = "Date"
    else:
        port_time = filtered_df.groupby(['Week_Number', 'Arrival port'])['Boxes'].sum().reset_index()
        x_axis = 'Week_Number'
        x_title = "Week Number"
    
    # Select specific ports or all
    port_selection = st.multiselect(
        "Select Ports to Analyze:",
        options=filtered_df['Arrival port'].unique(),
        default=filtered_df.groupby('Arrival port')['Boxes'].sum().sort_values(ascending=False).head(3).index.tolist()
    )
    
    if port_selection:
        port_time_filtered = port_time[port_time['Arrival port'].isin(port_selection)]
        
        fig = px.line(port_time_filtered, x=x_axis, y='Boxes', color='Arrival port',
                      title='Port Volume Over Time',
                      markers=True)
        fig.update_layout(xaxis_title=x_title, yaxis_title="Total Boxes")
        st.plotly_chart(fig, use_container_width=True)
    
    # Product mix by port
    st.subheader("Product Mix by Port")
    
    product_port = filtered_df.groupby(['Arrival port', 'Variety'])['Boxes'].sum().reset_index()
    
    selected_port = st.selectbox(
        "Select Port:",
        options=filtered_df['Arrival port'].unique()
    )
    
    port_products = product_port[product_port['Arrival port'] == selected_port]
    
    if not port_products.empty:
        fig = px.pie(port_products, values='Boxes', names='Variety',
                     title=f'Product Mix at {selected_port}')
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    # Transport mode by port
    st.subheader("Transport Modes by Port")
    
    transport_port = filtered_df.groupby(['Arrival port', 'Transport'])['Boxes'].sum().reset_index()
    
    fig = px.bar(transport_port, x='Arrival port', y='Boxes', color='Transport',
                 title='Transport Modes by Port',
                 barmode='stack')
    fig.update_layout(xaxis_title="Arrival Port", yaxis_title="Total Boxes")
    st.plotly_chart(fig, use_container_width=True)

elif selected_page == "Timeline Analysis":
    st.header("📅 Timeline Analysis")
    
    # Timeline metrics
    col1, col2, col3 = st.columns(3)
    
    # Get the busiest period
    monthly_volume = filtered_df.groupby(['Year', 'Month', 'Month_Name'])['Boxes'].sum().reset_index()
    if not monthly_volume.empty:
        busiest_month_idx = monthly_volume['Boxes'].idxmax()
        busiest_month = monthly_volume.loc[busiest_month_idx, 'Month_Name']
        busiest_year = monthly_volume.loc[busiest_month_idx, 'Year']
        
        with col1:
            st.metric("Busiest Month", f"{busiest_month} {busiest_year}")
        with col2:
            busiest_month_volume = monthly_volume.loc[busiest_month_idx, 'Boxes']
            st.metric("Busiest Month Volume", f"{busiest_month_volume:,}")
        with col3:
            avg_monthly_volume = monthly_volume['Boxes'].mean()
            st.metric("Avg Monthly Volume", f"{avg_monthly_volume:.1f}")
    
    # Volume by week chart
    st.subheader("Weekly Volume Analysis")
    
    weekly_volume = filtered_df.groupby('Week_Number')['Boxes'].sum().reset_index()
    fig = px.line(weekly_volume, x='Week_Number', y='Boxes',
                  title='Weekly Shipment Volume',
                  markers=True)
    fig.update_layout(xaxis_title="Week Number", yaxis_title="Total Boxes")
    st.plotly_chart(fig, use_container_width=True)
    
    # Monthly analysis
    st.subheader("Monthly Volume Analysis")
    
    monthly_volume = filtered_df.groupby(['Year', 'Month', 'Month_Name'])['Boxes'].sum().reset_index()
    monthly_volume = monthly_volume.sort_values(['Year', 'Month'])
    
    # Add month-year column for better display
    monthly_volume['Month-Year'] = monthly_volume['Month_Name'] + ' ' + monthly_volume['Year'].astype(str)
    
    fig = px.bar(monthly_volume, x='Month-Year', y='Boxes',
                 title='Monthly Shipment Volume',
                 color='Boxes')
    fig.update_layout(xaxis_title="Month", yaxis_title="Total Boxes")
    st.plotly_chart(fig, use_container_width=True)
    
    # Season comparison
    st.subheader("Season Comparison")
    
    season_volume = filtered_df.groupby('Season')['Boxes'].sum().reset_index()
    fig = px.bar(season_volume, x='Season', y='Boxes',
                 title='Volume by Season',
                 color='Boxes')
    fig.update_layout(xaxis_title="Season", yaxis_title="Total Boxes")
    st.plotly_chart(fig, use_container_width=True)
    
    # Timeline analysis by product
    st.subheader("Product Timeline Analysis")
    
    product_timeline_option = st.radio("Select Analysis Type:", ["Variety", "Transport Mode"], horizontal=True)
    
    if product_timeline_option == "Variety":
        # Top varieties to include
        top_varieties = filtered_df.groupby('Variety')['Boxes'].sum().sort_values(ascending=False).head(5).index
        variety_time = filtered_df[filtered_df['Variety'].isin(top_varieties)]
        variety_time = variety_time.groupby(['Week_Number', 'Variety'])['Boxes'].sum().reset_index()
        
        fig = px.line(variety_time, x='Week_Number', y='Boxes', color='Variety',
                      title='Weekly Volume by Top Varieties',
                      markers=True)
        fig.update_layout(xaxis_title="Week Number", yaxis_title="Total Boxes")
        st.plotly_chart(fig, use_container_width=True)
    else:
        transport_time = filtered_df.groupby(['Week_Number', 'Transport'])['Boxes'].sum().reset_index()
        
        fig = px.line(transport_time, x='Week_Number', y='Boxes', color='Transport',
                      title='Weekly Volume by Transport Mode',
                      markers=True)
        fig.update_layout(xaxis_title="Week Number", yaxis_title="Total Boxes")
        st.plotly_chart(fig, use_container_width=True)
    
    # Transit time trends if available
    if 'Transit_Days' in filtered_df.columns:
        st.subheader("Transit Time Trends")
        
        transit_weekly = filtered_df.groupby('Week_Number')['Transit_Days'].mean().reset_index()
        
        fig = px.line(transit_weekly, x='Week_Number', y='Transit_Days',
                      title='Average Transit Time by Week',
                      markers=True)
        fig.update_layout(xaxis_title="Week Number", yaxis_title="Average Transit Days")
        st.plotly_chart(fig, use_container_width=True) 