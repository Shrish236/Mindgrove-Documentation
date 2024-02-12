import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Sample data
df = px.data.iris()

# Initialize the Dash app
app = dash.Dash(__name__)
app.css.append_css({"external_url": "static/styles.css"})

# Define the layout for the home page
home_page_layout = html.Div([
    html.Div(
        className='home-header',
        children=[
            html.H1('Welcome to My Dash App', className='home-title'),
            html.Div([
                html.P('Explore our interactive visualizations.'),
                html.P('Click on the links below to navigate to different pages:', className='home-subtitle'),
                dcc.Link('Page 1 | ', href='/page-1', className='home-link'),
                dcc.Link('Page 2', href='/page-2', className='home-link'),
            ], className='home-text')
        ]
    ),
    html.Div([
        html.Img(src='https://via.placeholder.com/150', className='home-image'),
        html.P('Image Description', className='image-description')
    ], className='home-image-container')
], className='home-container')

# Define the layout for page 1
page_1_layout = html.Div([
    html.H1('Page 1'),
    dcc.Graph(
        id='page-1-graph',
        figure=px.scatter(df, x='sepal_width', y='sepal_length', color='species')
    ),
])

# Define the layout for page 2
page_2_layout = html.Div([
    html.H1('Page 2'),
    dcc.Graph(
        id='page-2-graph',
        figure=px.scatter(df, x='petal_width', y='petal_length', color='species')
    ),
])

# Define the callback to switch between pages
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page-1':
        return page_1_layout
    elif pathname == '/page-2':
        return page_2_layout
    else:
        return home_page_layout

# Define the app layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
