# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = int(spacex_df['Payload Mass (kg)'].max())
min_payload = int(spacex_df['Payload Mass (kg)'].min())
spacex_sites = spacex_df['Launch Site'].unique()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                                options=[{'label': 'All Sites', 'value': 'ALL'},
                                                    {'label': spacex_sites[0], 'value': spacex_sites[0]},
                                                    {'label': spacex_sites[1], 'value': spacex_sites[1]},
                                                    {'label': spacex_sites[2], 'value': spacex_sites[2]},
                                                    {'label': spacex_sites[3], 'value': spacex_sites[3]}
                                                ],
                                                value='ALL',
                                                placeholder='Select a launch site',
                                                searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    marks={i: str(i) for i in range(0, 10001, 2500)},
                                    value=[2500, 8000]
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        fig = px.pie(filtered_df,
            values='class', 
            names='Launch Site', 
            title='Total number of succesfull launches per site'
        )
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        site_counts = filtered_df['class'].value_counts().reset_index()
        site_counts.columns = ['Outcome', 'Count']
        site_counts['Outcome'] = site_counts['Outcome'].replace({1: 'Success', 0: 'Failure'})
        fig = px.pie(
            site_counts,
            values='Count',
            names='Outcome',
            title=f'Succesfull vs. failed launches for site: {entered_site}'
        )
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter_chart(entered_site, payload_range):
    # Get payload selection from slider
    plmin, plmax = payload_range
    # Filter df
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= plmin) & (spacex_df['Payload Mass (kg)'] <= plmax)]

    if entered_site == 'ALL':
        # Use all launch sites, filtered by payload range
        fig = px.scatter(
            filtered_df, 
            x='Payload Mass (kg)', 
            y='class',
            color='Booster Version Category',
            title='Payload vs. outcome for all launch sites',
            labels={'class': 'Launch outcome (0=failure, 1=success)'}
        )
    else:
        # Filter by the selected site too
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Payload vs. outcome for site: {entered_site}',
            labels={'class': 'Launch outcome (0=failure, 1=success)'}
        )

    return fig

# Run the app
if __name__ == '__main__':
    app.run()
