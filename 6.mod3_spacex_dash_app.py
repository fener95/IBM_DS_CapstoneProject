# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
        ] + [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    
    
    
    # Pie chart component
    dcc.Graph(id='success-pie-chart'),
# Range Slider for payload
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={0: '0', 1000: '1000', 2500: '2500', 5000:'5000', 7500:'7500', 10000: '10000'},
        value=[spacex_df['Payload Mass (kg)'].min(), spacex_df['Payload Mass (kg)'].max()]
    ),
    # Scatter plot component
    dcc.Graph(id='success-payload-scatter-chart'),

])

# Callback function for rendering success-pie-chart based on selected site dropdown
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
    if entered_site == 'ALL':
        fig = px.pie(filtered_df, values='class', names='Launch Site', title='Total Success Launches')
    else:
        success_count = site_df['class'].sum()
        total_count = len(site_df)
        success_rate = success_count / total_count
        fig = px.pie(site_df, values=[success_count, total_count - success_count], names=['Success', 'Failure'], title=f'Success Launches for {entered_site}')
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), margin=dict(l=0, r=0, t=0, b=0))
        fig.add_annotation(x=0.5, y=0.5, text=f"{success_rate:.0%}", font=dict(size=24), showarrow=False, xref="paper", yref="paper")
    return fig

# Callback function for rendering success-payload-scatter-chart scatter plot
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id="payload-slider", component_property="value")]
)
def get_scatter_plot(selected_site, selected_payload_range):
    filtered2_df = spacex_df

    # Filter by selected site
    if selected_site != 'ALL':
        filtered2_df = filtered2_df[filtered2_df['Launch Site'] == selected_site]

    # Filter by selected payload range
    filtered2_df = filtered2_df[
        (filtered2_df['Payload Mass (kg)'] >= selected_payload_range[0]) &
        (filtered2_df['Payload Mass (kg)'] <= selected_payload_range[1])
    ]

    fig = px.scatter(
        filtered2_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Payload vs. Mission Outcome',
        labels={'class': 'Mission Outcome'}
    )

    return fig
if __name__ == '__main__':
    app.run_server()