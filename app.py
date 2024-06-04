import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load and clean the data
file_path = './db.xlsx'  # Update the file path to your Excel file

# Read the Excel file
df = pd.read_excel(file_path, engine='openpyxl')

# Remove rows with NaN values in key columns for dropdowns
df = df.dropna(subset=['Nationalité', 'Sexe', 'Projet', 'Région', 'Localité', 'Variété'])

# Standardize text data to lowercase and normalize text
df['Nationalité'] = df['Nationalité'].str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
df['Sexe'] = df['Sexe'].str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
df['Projet'] = df['Projet'].str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
df['Région'] = df['Région'].str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
df['Localité'] = df['Localité'].str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
df['Variété'] = df['Variété'].str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

# Map similar nationality values to a common standard
df['Nationalité'] = df['Nationalité'].replace({
    'etrangere': 'etranger'
})

# Map similar gender values to a common standard
df['Sexe'] = df['Sexe'].replace({
    'homme': 'male', 'masculin': 'male', 'm': 'male',
    'femme': 'female', 'feminin': 'female', 'féminin': 'female', 'f': 'female'
})

# Expand rows where 'Variété' has multiple values, handle 'et autres'
df = df.assign(Variété=df['Variété'].str.split(',| et autres| et autre| et')).explode('Variété')

# Trim whitespace and clean 'Variété' values
df['Variété'] = df['Variété'].str.strip()

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=['https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css'])

# Define the layout of the app
app.layout = html.Div(className='container-fluid', children=[
    html.H1("Interactive Dashboard with Multiple Filters", className='text-center my-4'),
    
    # Section 1: Region Pie Chart
    html.Div(className='section mt-4', children=[
        html.Div(className='row', children=[
            html.Div(className='col-md-12', children=[
                dcc.Graph(id='region-pie-chart')
            ])
        ])
    ]),

    # Section 2: Localité Chart with Region Filter
    html.Div(className='section mt-4', children=[
        html.Div(className='row', children=[
            html.Div(className='col-md-3', children=[
                html.Div(className='dcc-dropdown', children=[
                    html.Label("Select Region:", className='form-label'),
                    dcc.Dropdown(
                        id='region-filter',
                        options=[{'label': region, 'value': region} for region in df['Région'].unique() if region],
                        value=None,
                        placeholder="Select region",
                        className='form-control'
                    )
                ])
            ]),
            html.Div(className='col-md-9', children=[
                dcc.Graph(id='localite-bar-chart')
            ])
        ])
    ]),

    # Section 3: Variété Bar Chart
    html.Div(className='section mt-4', children=[
        html.Div(className='row', children=[
            html.Div(className='col-md-12', children=[
                dcc.Graph(id='variete-bar-chart')
            ])
        ])
    ]),

    # Section 4: Age Distribution Chart with Filters
    html.Div(className='section mt-4', children=[
        html.Div(className='row', children=[
            html.Div(className='col-md-3', children=[
                html.Div(className='dcc-dropdown', children=[
                    html.Label("Select Nationality:", className='form-label'),
                    dcc.Dropdown(
                        id='nationality-filter',
                        options=[{'label': nationality, 'value': nationality} for nationality in df['Nationalité'].unique() if nationality],
                        value=None,
                        multi=True,
                        placeholder="Select nationality",
                        className='form-control'
                    )
                ]),
                html.Div(className='dcc-dropdown', children=[
                    html.Label("Select Gender:", className='form-label'),
                    dcc.Dropdown(
                        id='gender-filter',
                        options=[{'label': gender, 'value': gender} for gender in df['Sexe'].unique() if gender],
                        value=None,
                        multi=True,
                        placeholder="Select gender",
                        className='form-control'
                    )
                ]),
                html.Div(className='dcc-dropdown', children=[
                    html.Label("Select Project:", className='form-label'),
                    dcc.Dropdown(
                        id='project-filter',
                        options=[{'label': project, 'value': project} for project in df['Projet'].unique() if project],
                        value=None,
                        multi=True,
                        placeholder="Select project",
                        className='form-control'
                    )
                ])
            ]),
            html.Div(className='col-md-9', children=[
                dcc.Graph(id='age-distribution-chart')
            ])
        ])
    ])
])

# Define the callback to update the charts based on the dropdown selections
@app.callback(
    [Output('age-distribution-chart', 'figure'),
     Output('region-pie-chart', 'figure'),
     Output('localite-bar-chart', 'figure'),
     Output('variete-bar-chart', 'figure')],
    [Input('nationality-filter', 'value'),
     Input('gender-filter', 'value'),
     Input('project-filter', 'value'),
     Input('region-filter', 'value')]
)
def update_charts(selected_nationalities, selected_genders, selected_projects, selected_region):
    # Filter the data for age distribution, region pie chart, and variety bar chart
    filtered_df = df.copy()
    
    if selected_nationalities:
        filtered_df = filtered_df[filtered_df['Nationalité'].isin(selected_nationalities)]
    
    if selected_genders:
        filtered_df = filtered_df[filtered_df['Sexe'].isin(selected_genders)]
    
    if selected_projects:
        filtered_df = filtered_df[filtered_df['Projet'].isin(selected_projects)]
    
    # Age distribution chart
    color_discrete_map = {'male': 'blue', 'female': 'red'}
    
    age_fig = px.histogram(
        filtered_df, 
        x='Age', 
        nbins=20, 
        title='Age Distribution',
        labels={'Age': 'Age (years)', 'count': 'Number of Individuals'},
        color='Sexe',
        color_discrete_map=color_discrete_map,
        barmode='group'
    )
    
    age_fig.update_layout(
        xaxis_title='Age (years)',
        yaxis_title='Number of Individuals',
        title={'x':0.5, 'xanchor': 'center'},
        template='plotly_dark'
    )
    
    age_fig.update_traces(marker_line_width=1.5, marker_line_color='black')
    
    # Region pie chart
    region_fig = px.pie(
        filtered_df,
        names='Région',
        title='Distribution by Région'
    )
    
    region_fig.update_layout(
        title={'x':0.5, 'xanchor': 'center'},
        template='plotly_dark'
    )
    
    # Filter data for localite chart based on selected region
    localite_filtered_df = df.copy()
    if selected_region:
        localite_filtered_df = localite_filtered_df[localite_filtered_df['Région'] == selected_region]
    
    # Filter out Localités with less than 10 occurrences
    localite_counts = localite_filtered_df['Localité'].value_counts()
    valid_localites = localite_counts[localite_counts >= 10].index
    localite_filtered_df = localite_filtered_df[localite_filtered_df['Localité'].isin(valid_localites)]
    
    # Localité bar chart
    localite_fig = px.bar(
        localite_filtered_df,
        x=localite_filtered_df['Localité'].value_counts().index,
        y=localite_filtered_df['Localité'].value_counts().values,
        title='Distribution by Localité'
    )
    
    localite_fig.update_layout(
        xaxis_title='Localité',
        yaxis_title='Count',
        title={'x': 0.5, 'xanchor': 'center'},
        template='plotly_dark'
    )
    
    # Variété bar chart
    variete_counts = filtered_df['Variété'].value_counts()
    variete_fig = px.bar(
        variete_counts,
        x=variete_counts.index,
        y=variete_counts.values,
                title='Distribution by Variété'
    )
    
    variete_fig.update_layout(
        xaxis_title='Variété',
        yaxis_title='Count',
        title={'x':0.5, 'xanchor': 'center'},
        template='plotly_dark'
    )
    
    return age_fig, region_fig, localite_fig, variete_fig

# Run the app
if __name__ == '__main__':
    app.run_server()

