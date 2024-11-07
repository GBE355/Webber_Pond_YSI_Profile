# Webber Pond YSI Profile Dashboard

This repository contains a Dash web application for visualizing water quality data from YSI sensors in Webber Pond. The app provides an interactive map with sample sites, and each site links to depth profile plots for various parameters, such as chlorophyll, phycocyanin, temperature, dissolved oxygen, pH, and ORP.

## Features

- Interactive map of sample sites with satellite basemap
- Depth profile plots for selected water quality parameters
- Grouped depth data for more consistent trend visualization

## Project Structure

- `Webber Pond/Raw`: Raw .csv files for each sample site
- `Webber Pond/Raw/YSI Geo Split`: Output files grouped by geolocation
- `Webber Pond/Output/Plots`: Directory for storing profile plots
- `Webber Pond/Output/Geo`: Unused, intended for future GIS files
- `Webber Pond/Output/Tables`: Unused, intended for future data tables

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/GBE355/Webber_Pond_YSI_Profile.git
cd Webber_Pond_YSI_Profile
2. Install Dependencies
Ensure you have Python installed (3.8 or later recommended). Install the required packages listed in requirements.txt:

bash
Copy code
pip install -r requirements.txt
3. Set Up Environment Variables
You need a Mapbox access token for displaying maps. Set this as an environment variable called MAPBOX_TOKEN:

For Windows:

bash
Copy code
set MAPBOX_TOKEN=your_mapbox_token_here
For macOS/Linux:

bash
Copy code
export MAPBOX_TOKEN=your_mapbox_token_here
Alternatively, you can set a default token in the code:

python
Copy code
mapbox_token = os.getenv("MAPBOX_TOKEN", "your_default_token_here")
4. Run the App
Start the app with:

bash
Copy code
python Webber_Pond_YSI_Profile.py
Then, go to http://127.0.0.1:8050 in your browser to view the app.

Deployment
To deploy this app on Render or another cloud service:

Procfile: Ensure you have a Procfile that specifies the web process, such as:

makefile
Copy code
web: gunicorn Webber_Pond_YSI_Profile:app
Gunicorn: Make sure gunicorn is in your requirements.txt to allow Render to use it.

Environment Variables: Set the MAPBOX_TOKEN as an environment variable in your Render settings.

Repository Structure: Render will use the current directory as base_dir, so all file paths should be relative or use os.path.join(os.getcwd(), ...) for flexibility.

Usage
Select a Parameter: Use the dropdown to choose a water quality parameter.
View the Map: Click on any site marker to view depth profiles.
Depth Profile Plot: Displays a scatter plot of the selected parameter, averaged by depth for a clearer trend view.
Requirements
The main dependencies are:

pandas: For data manipulation and CSV handling
numpy: For numerical operations
dash & plotly: For the interactive web application and visualizations
geopy: For calculating distances between GPS coordinates
Contributing
Feel free to fork this repository and submit pull requests. Ensure any new dependencies are added to requirements.txt.

License
This project is open-source and available under the MIT License.

Acknowledgments
Thanks to Mapbox for map visualizations and Plotly for interactive plots.

javascript
Copy code

This Markdown format (`README.md`) will render well on GitHub, providing clear sections and a user-friendly layout. Save it as `README.md` in your project repository.