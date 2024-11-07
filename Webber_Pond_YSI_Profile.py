# Data manipulation and analysis
import pandas as pd  # Used for data manipulation and analysis
import numpy as np  # Used for numerical computations and array manipulations

# Visualization libraries
import matplotlib.pyplot as plt  # Used for plotting static graphs
import seaborn as sns  # Enhances Matplotlib with more statistical plots
import plotly.express as px  # Used for creating interactive plots with Plotly Express
import plotly.graph_objs as go  # Provides fine-grained control over Plotly graphs

# Date and time handling
import datetime  # Used for date and time manipulations
from calendar import month_name as mn  # Used to get month names from month numbers
import matplotlib.dates as mdates  # Date-related plotting utilities in Matplotlib
from matplotlib.dates import DateFormatter  # Formats dates on Matplotlib plots

# Geospatial tools
from geopy.distance import geodesic  # Used to calculate distances between geospatial coordinates

# Data export and input/output
import os  # Used for operating system interactions, such as file and directory management
import glob  # Used to retrieve files matching a specified pattern

# Warnings and inline plotting
import warnings  # Used to handle warnings
warnings.filterwarnings('ignore')  # Suppresses warning messages

# Dash for interactive web applications
import dash  # Used to create web applications with Python
from dash import dcc, html  # Provides core components and HTML components for Dash apps
from dash.dependencies import Input, Output  # Used to link components in Dash apps with callback functions

# Plotly and interactive data visualizations in Dash
import plotly.express as px  # For quick and easy interactive plots
import plotly.graph_objs as go  # For more detailed control over Plotly figures

# Regular expressions
import re  # Used for pattern matching in strings

# Base64 encoding for embedding images
from io import BytesIO  # Used for in-memory byte streams (e.g., for images)
import base64  # Used for encoding binary data (e.g., images) as base64 strings

raw_dir = r"C:\YSI Temp\Webber Pond\Raw"  # Raw .csv files should be stored here
input_dir = os.path.join(raw_dir, 'YSI Geo Split')  # Where to read the geo grouped files
output_dir = r"C:\YSI Temp\Webber Pond\Output"  # Master directory of compiled files
plots_dir = os.path.join(output_dir, 'Plots')
geo_dir = os.path.join(output_dir, 'Geo')
tables_dir = os.path.join(output_dir, 'Tables')

# Automatically collect all variables ending with '_dir' into a list
directories = [value for name, value in globals().items() if name.endswith('_dir')]

def ensure_directory_exists(directory):
    """Check if a directory exists, and create it if it does not."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")
    else:
        print(f"Directory already exists: {directory}")

# Verify each directory exists
for directory in directories:
    ensure_directory_exists(directory)

# Define the distance threshold
distance_threshold_m = 50

# Initialize an empty DataFrame to hold all data
master_df = pd.DataFrame()

# Counter for the number of files loaded
file_count = 0

# Loop through all CSV files in raw_dir and append their contents to master_df
for file_name in os.listdir(raw_dir):
    if file_name.endswith('.csv'):
        file_path = os.path.join(raw_dir, file_name)
        df = pd.read_csv(file_path, encoding='ISO-8859-1', on_bad_lines='skip')
        master_df = pd.concat([master_df, df], ignore_index=True)
        file_count += 1

# Print the count of loaded files and preview the first 5 rows of the master DataFrame
print(f"Loaded {file_count} files")
print(master_df.head(5))

mapbox_token = "pk.eyJ1IjoiZG9uY2FybG9zIiwiYSI6ImNraXliMnk5aDNtcTgycHAzNjFlODd5N3EifQ.FgYMucBPzxo79iYOvttr1Q"

# Function to calculate distance between two latitude/longitude points in meters
def distance_in_meters(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).meters

# Initialize an empty list to hold the grouped DataFrames
geo_grouped_dfs = []

# Counter for number of files created
file_count = 0

# Drop any rows with NaN values in Lat or Lon columns from master_df (assumed to be previously loaded)
df_cleaned = master_df.dropna(subset=['Lat', 'Lon'])

while not df_cleaned.empty:
    # Take the first point
    first_point = df_cleaned.iloc[0]
    lat1, lon1 = first_point['Lat'], first_point['Lon']
    
    # Find all points within distance_threshold_m meters of the first point
    mask = df_cleaned.apply(lambda row: distance_in_meters(lat1, lon1, row['Lat'], row['Lon']) <= distance_threshold_m, axis=1)
    group = df_cleaned[mask]
    
    # Append the group to the list of grouped DataFrames
    geo_grouped_dfs.append(group)
    
    # Drop the grouped points from the original DataFrame
    df_cleaned = df_cleaned[~mask]
    
    # Determine mode for Lat and Lon to name the file
    mode_lat = np.round(group['Lat'].mode()[0], 5)
    mode_lon = np.round(group['Lon'].mode()[0], 5)
    
    # Define the output file name with mode Lat and Lon values
    filename = f"{mode_lat}Lat_{mode_lon}Lon.csv"
    output_path = os.path.join(input_dir, filename)
    
    # Drop the 'Lat' and 'Lon' columns from the group DataFrame
    group.drop(columns=['Lat', 'Lon'], inplace=True)
    
    # Remove empty columns (columns with all NaN values)
    group.dropna(axis=1, how='all', inplace=True)
    
    # Save the group as a CSV file without Lat, Lon, and empty columns
    group.to_csv(output_path, index=False)
    
    # Increment the file counter
    file_count += 1

# Print the total count of files created
print(f"{file_count} files created in {input_dir}")

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Water Quality Map with Profile Plots"

# Directory where CSV files are stored
input_dir = r"C:\YSI Temp\Webber Pond\Raw\YSI Geo Split"

# Define available parameters for the dropdown
parameters = ["Chl ug/L", "PC ug/L", "°C", "DO mg/L", "pH", "ORP mV"]

# Regular expression pattern to extract latitude and longitude from filename
filename_pattern = re.compile(r"(?P<lat>-?\d+\.\d+)Lat_(?P<lon>-?\d+\.\d+)Lon\.csv")

# Load and process all files
site_data = []
for file_name in os.listdir(input_dir):
    if file_name.endswith('.csv'):
        match = filename_pattern.match(file_name)
        if match:
            lat = float(match.group("lat"))
            lon = float(match.group("lon"))
            file_path = os.path.join(input_dir, file_name)
            df = pd.read_csv(file_path)

            # Store data for each site in a list with latitude, longitude, and file path
            site_data.append({"Latitude": lat, "Longitude": lon, "FilePath": file_path})

# Sort the sites by latitude (south to north)
site_data = sorted(site_data, key=lambda x: x["Latitude"])

# Add sequential labels to each site
for i, site in enumerate(site_data, start=1):
    site["Sample Site"] = f"Sample Site {i}"

# Load the data for "Sample Site 1" as default
default_site = site_data[0]  # Sample Site 1

# Function to create a scatter plot for a site and parameter with averaged values by depth
def generate_profile_plot(df, parameter):
    if parameter not in df.columns or 'DEP m' not in df.columns:
        print(f"Parameter '{parameter}' or 'DEP m' not found in DataFrame columns: {df.columns}")
        return go.Figure()

    # Group by 'DEP m' and calculate the mean of the selected parameter at each depth
    averaged_df = df.groupby('DEP m')[parameter].mean().reset_index()

    # Create a scatter plot
    fig = px.scatter(
        averaged_df,
        x=parameter,
        y="DEP m",
        title=f"{parameter} Profile",
        labels={parameter: parameter, "DEP m": "Depth (m)"}
    )
    
    fig.update_yaxes(autorange="reversed")  # Invert y-axis for depth
    
    return fig

# Create the layout of the Dash app
app.layout = html.Div([
    html.H1("Water Quality Map with Sample Site Profiles"),

    # Dropdown for parameter selection
    html.Div([
        html.Label("Select Parameter for Profile Plot:"),
        dcc.Dropdown(
            id="parameter-dropdown",
            options=[{"label": param, "value": param} for param in parameters],
            value="Chl ug/L"  # Default value
        )
    ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),

    # Parent container for map and profile plot
    html.Div(
        children=[
            # Map on the left
            dcc.Graph(id="map", style={'width': '55%', 'display': 'inline-block', 'height': '75vh'}),
            
            # Profile plot on the right
            dcc.Graph(id="profile-plot", style={'width': '40%', 'display': 'inline-block', 'height': '75vh'})
        ],
        style={'display': 'flex', 'justify-content': 'space-between'}
    )
])

# Update the map figure
@app.callback(
    Output("map", "figure"),
    Input("parameter-dropdown", "value")
)
def update_map(selected_parameter):
    # Prepare data for the map
    map_df = pd.DataFrame(site_data)

    # Create the map figure
    map_fig = px.scatter_mapbox(
        map_df,
        lat="Latitude",
        lon="Longitude",
        hover_name="Sample Site",
        title="Sample Site Locations",
        zoom=12  # Set zoom level closer
    )
    map_fig.update_traces(marker=dict(size=10, color="blue", opacity=0.8))

    # Mapbox settings
    map_fig.update_layout(
        mapbox_style="satellite",
        mapbox_accesstoken=mapbox_token,
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    return map_fig

# Update the profile plot when a site is clicked on the map or when the app loads
@app.callback(
    Output("profile-plot", "figure"),
    [Input("map", "clickData"), Input("parameter-dropdown", "value")]
)
def update_profile_plot(clickData, selected_parameter):
    # If no site is selected (on initial load), default to "Sample Site 1"
    if clickData is None:
        df_default = pd.read_csv(default_site["FilePath"])
        return generate_profile_plot(df_default, selected_parameter)

    # Get the coordinates of the clicked point
    lat = clickData["points"][0]["lat"]
    lon = clickData["points"][0]["lon"]

    # Find the file corresponding to the clicked site
    selected_site = next((site for site in site_data if site["Latitude"] == lat and site["Longitude"] == lon), None)
    if selected_site is None:
        print(f"No data found for Latitude: {lat}, Longitude: {lon}")
        return go.Figure()

    # Load the site's data and create the profile plot
    df = pd.read_csv(selected_site["FilePath"])
    profile_plot = generate_profile_plot(df, selected_parameter)

    return profile_plot

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
