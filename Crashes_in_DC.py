import requests
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html
import dash

# URL for the CSV file
url = "https://opendata.dc.gov/api/download/v1/items/70392a096a8e431381f1f692aaa06afd/csv?layers=24"

# Fetch CSV content with requests and read it into pandas
response = requests.get(url, verify=False)  # disable SSL verification
response.raise_for_status()  # raises an error if the download fails
data = response.content

# Load CSV data into pandas
from io import StringIO
df = pd.read_csv(StringIO(data.decode('utf-8')), parse_dates=["REPORTDATE"], low_memory=False)

# Now you can continue with your original data processing code
df = df[(df['REPORTDATE'].dt.year >= 2020) & (df['REPORTDATE'].dt.year <= 2025)]

# Extract year-month for monthly analysis
df['YearMonth'] = df['REPORTDATE'].dt.to_period('M').astype(str)

# Injury-related columns
injury_cols = [
    'MAJORINJURIES_BICYCLIST', 'MINORINJURIES_BICYCLIST', 'UNKNOWNINJURIES_BICYCLIST',
    'FATAL_BICYCLIST', 'MAJORINJURIES_DRIVER', 'MINORINJURIES_DRIVER', 'UNKNOWNINJURIES_DRIVER',
    'FATAL_DRIVER', 'MAJORINJURIES_PEDESTRIAN', 'MINORINJURIES_PEDESTRIAN',
    'UNKNOWNINJURIES_PEDESTRIAN', 'FATAL_PEDESTRIAN',
    'FATALPASSENGER', 'MAJORINJURIESPASSENGER', 'MINORINJURIESPASSENGER',
    'UNKNOWNINJURIESPASSENGER', 'MAJORINJURIESOTHER', 'MINORINJURIESOTHER',
    'UNKNOWNINJURIESOTHER', 'FATALOTHER'
]

# Fill NaNs and calculate total injuries
df[injury_cols] = df[injury_cols].fillna(0)
df['TotalInjuries'] = df[injury_cols].sum(axis=1)

# Monthly summary for time series
monthly = df.groupby('YearMonth').agg({'CRIMEID': 'count', 'TotalInjuries': 'sum'}).reset_index()
monthly.rename(columns={'CRIMEID': 'Incidents'}, inplace=True)

# Classify crashes by severity for drivers
df['CrashSeverity'] = 'Minor'
df.loc[df['FATAL_DRIVER'] > 0, 'CrashSeverity'] = 'Fatal'
df.loc[df['MAJORINJURIES_DRIVER'] > 0, 'CrashSeverity'] = 'Major'

# Initialize the Dash app
app = Dash(__name__)
app.title = "DC Traffic Crash Dashboard"

# Dash layout
app.layout = html.Div(style={'fontFamily': 'Arial', 'padding': '20px'}, children=[
    html.H1("DC Traffic Accident Dashboard", style={'textAlign': 'center'}),

    html.Div([
        html.P("This dashboard provides a comprehensive overview of traffic accidents in Washington, DC, from 2020 to 2025. Filtered through severity of accident (Minor, Major, or Fatal) the visualizations helps to identify patterns, severity trends, and areas with high accident rates. The dataset covers various crash severities, locations, and high crash times of the year that helps to offer insights into how traffic incidents have evolved over time."),
    ], style={'textAlign': 'center', 'marginBottom': '40px'}),

    html.Div([
        html.H3("Filter by Crash Severity"),
        dcc.Dropdown(
            id='severity-dropdown',
            options=[
                {'label': 'All', 'value': 'All'},
                {'label': 'Fatal', 'value': 'Fatal'},
                {'label': 'Major', 'value': 'Major'},
                {'label': 'Minor', 'value': 'Minor'}
            ],
            value='All',
        ),
    ], style={'marginBottom': '20px'}),

    html.Div([
        html.H3("1. Heatmap: Incidents by Ward and Month"),
        html.P("The heatmap visualizes the concentration of traffic incidents across different wards of Washington, DC, by month. The color intensity represents the frequency of accidents. Darker areas indicate higher incident rates."),
        dcc.Graph(figure=px.density_heatmap(
            df, x="YearMonth", y="WARD", title="Heatmap of Incidents",
            color_continuous_scale="Inferno"
        ))
    ], style={'marginBottom': '40px'}),

    html.Div([
        html.H3("2. Map: Accident Locations by Severity"),
        html.P("This map displays the locations of accidents across the city, categorized by severity (Fatal, Major, Minor). The map uses color coding to differentiate between crash severity levels: red for fatal crashes, orange for major injuries, and green for minor incidents."),
        dcc.Graph(id='map')
    ], style={'marginBottom': '40px'}),

    html.Div([
        html.H3("3. Bar Chart: Total Accidents by Ward"),
        html.P("The bar chart presents the total number of accidents for each ward in Washington, DC. Each bar represents a ward, and the color coding highlights the relative number of incidents in different areas. This visual provides an overview of which wards have the highest accident rates."),
        dcc.Graph(figure=px.histogram(
            df, x="WARD", title="Accidents per Ward",
            color="WARD", color_discrete_sequence=px.colors.qualitative.Bold
        ))
    ], style={'marginBottom': '40px'}),

    html.Div([
        html.H3("4. Time Series: Monthly Incidents & Injuries"),
        html.P("This time series chart shows the trends in traffic incidents and total injuries over time, broken down by month. It provides a clear view of how accident frequency and injury rates have evolved, helping to identify potential spikes or declines in accidents, as well as trends in the severity of injuries over the years."),
        dcc.Graph(figure=px.line(
            monthly, x="YearMonth", y=["Incidents", "TotalInjuries"],
            title="Monthly Incidents and Injuries Over Time",
            markers=True
        ))
    ]),

    html.Div([
        html.H3("Data Source"),
        html.P("The data used in this dashboard is sourced from Data.gov, 'Crashes in DC'."),
    ], style={'marginTop': '40px'})
])

# Callback to update the map based on severity dropdown
@app.callback(
    dash.dependencies.Output('map', 'figure'),
    [dash.dependencies.Input('severity-dropdown', 'value')]
)
def update_map(severity):
    # Filter data based on the selected severity
    filtered_data = df[df['CrashSeverity'] == severity] if severity != 'All' else df
    return px.scatter_mapbox(filtered_data, lat="LATITUDE", lon="LONGITUDE", color="CrashSeverity",
                             color_discrete_map={"Fatal": "red", "Major": "orange", "Minor": "green"},
                             mapbox_style="carto-positron", zoom=11, title="Accident Locations by Severity")

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
