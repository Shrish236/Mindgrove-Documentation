# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import json

table = ""
# Incorporate data
# df = pd.read_csv('static/Employee.csv')

# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, 'static/styles.css'], suppress_callback_exceptions=True)

# App layout
# app.layout = html.Div([
#     html.H1('Graphical Representation', className='text-primary m-2'),
#     html.Hr(),
#     html.H6('X-Axis data', className='text-secondary px-3'),
#     dbc.RadioItems(options=df.columns, value=df.columns[0], id='controls-and-radio-item', className='m-4', inline=True),
#     html.H6('Y-Axis data', className='text-secondary px-3'),
#     dbc.RadioItems(options=df.columns, value=df.columns[0], id='y-axis-selection', className='m-4', inline=True),
#     html.H6('Type of Graph', className='text-secondary px-3'),
#     dbc.RadioItems(options=['Bar', 'Line', 'Histogram', 'Scatter'], value='Bar', id='graph-type', className='m-4', inline=True),
#     # dash_table.DataTable(data=df.to_dict('records'), page_size=df.shape[0]),
#     dcc.Graph(figure={}, id='controls-and-graph')
# ])

items = [
    dbc.DropdownMenuItem("JSON Format", id="json_format"),
    dbc.DropdownMenuItem(divider=True),
    dbc.DropdownMenuItem("Local CSV File", id="csv_local"),
    dbc.DropdownMenuItem(divider=True),
    dbc.DropdownMenuItem("Link to CSV File", id="csv_remote"),
]

graph_data_json = html.Div([
    html.P(
        "Paste your JSON data here",
        className="card-text",
    ),
    dbc.Textarea(
        size="lg",
        placeholder="{ \tkey : value\t}",
        className='custom-textarea',
        style={
            'width':'100%',
            'font-size' : '15px',
        },
        valid=None,
        id='json-input'
    ),
    dbc.FormText(
        "You can expand the textbox if needed!",
        color="secondary"
    ),
    html.Div([
        dbc.Button("Submit", outline=True, color="primary", id='submit-button-json', href='graph-page'),
    ], className='d-flex justify-content-center p-2 pt-4'),
], id='2')

graph_data_local = html.Div([
    html.P(
        "Upload your local csv file here",
        className="card-text",
    ),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files', className='fst-italic font-decoration-underline')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=False
    ),
    dbc.FormText(
        "Only .csv files are supported!",
        color="danger"
    ),
    html.Div([
        dbc.Button("Submit", outline=True, color="primary", id='submit-button-local', href='/graph-page'),
    ], className='d-flex justify-content-center p-2 pt-4'),
], id='1')

graph_data_remote = html.Div([
    html.P(
        "Paste the link to remote CSV file here",
        className="card-text",
    ),
    dbc.Input(placeholder="Eg: https://www.drive.google.com/file", type="text", id='remote-link'),
    dbc.FormText("Make sure the file is given open access!", className='text-danger'),
    html.Div([
        dbc.Button("Submit", outline=True, color="primary", id='submit-button-remote', href='/graph-page'),
    ], className='d-flex justify-content-center p-2 pt-4'),
], id='3')

home_page_layout = html.Div([
    html.Div([
        html.Div([
            html.P('Graph Viewer', className='fs-3 fw-medium text-center text-primary', style={
                'font-family': 'Arial',
            })
        ], className='row text-center p-4'),
        html.Div([
            html.Div([
                html.Div([
                    html.P("Input the following details", className='fs-5 fw-normal text-primary', style={
                        'font-family': 'Arial',
                    })
                ]),
                html.Div([
                    html.Div([
                        dbc.Label("Select your data format", html_for="example-email"),
                        dbc.DropdownMenu(
                            label="Data Format", children=items
                        ),
                        dbc.FormText(
                            "Appropriate data format must be chosen to plot graphs accordingly",
                            color="secondary"
                        ),
                    ], className='py-2'),
                    html.Hr(),
                    html.Div([
                        dbc.Label("Select the required types of graphs", html_for="example-email"),
                        html.Div([
                            dbc.Checklist(
                                id="checklist-selected-style",
                                options=[
                                    {"label": "Scatter plot", "value": 1},
                                    {"label": "Line plot", "value": 2},
                                    {"label": "Bar graph", "value": 3},
                                ],
                                label_checked_style={"color": "red"},
                                input_checked_style={
                                    "backgroundColor": "#fa7268",
                                    "borderColor": "#ea6258",
                                },
                            ),
                            dbc.Checklist(
                                id="checklist-selected-style1",
                                options=[
                                    {"label": "Histogram", "value": 4},
                                    {"label": "Pie chart", "value": 5},
                                    {"label": "Distplot", "value": 6},
                                ],
                                label_checked_style={"color": "red"},
                                input_checked_style={
                                    "backgroundColor": "#fa7268",
                                    "borderColor": "#ea6258",
                                },
                            ),
                        ], className='d-flex gap-3'),
                        dbc.FormText(
                            "You can select multiple options!",
                            color="secondary"
                        ),
                    ], className='py-2'),
                ])
            ], className='col ps-5', style={
                'border-right': '1px solid #7A7B7C',
            }),
            html.Div([
                html.Div([
                    dbc.Card(
                        [
                            dbc.CardHeader("Graph data"),
                            dbc.CardBody(
                                [
                                    html.H5("Input your data to be visualized", className="card-title"),
                                    html.Div(
                                        # [
                                        # html.P(
                                        #     "Paste the link to remote CSV file here",
                                        #     className="card-text",
                                        # ),
                                        # dbc.Input(placeholder="Eg: https://www.drive.google.com/file", type="text"),
                                        # dbc.FormText("Make sure the file is given open access!", className='text-danger'),
                                    # ], 
                                    id='data-format'),
                                    
                                ]
                            ),
                        ],
                        color="primary", 
                        outline=True,
                        style={
                            'height':'auto',
                            'width' : '100%',
                        }
                    )
                ], className='d-flex align-items-center h-100'),
                html.P(id='dummy-tag'),
            ], className='col px-4')
        ], className='row')
    ], className='container min-vh-75 bg-light rounded-1')
], className='d-flex bg-secondary min-vh-100 min-vw-100 px-3 py-5 justify-content-center')
selection_state = [0, 0, 0]
# Add controls to build the interaction
# @callback(
#         Output(component_id='controls-and-graph', component_property='figure'),
#     [
#         Input(component_id='y-axis-selection', component_property='value'),
#         Input(component_id='controls-and-radio-item', component_property='value'),
#         Input(component_id='graph-type', component_property='value'),
#     ]
# )
# app.layout = home_page_layout
@callback(
        Output('data-format', 'children'), 
        [
            Input(component_id='json_format', component_property='n_clicks'), 
            Input('csv_local', 'n_clicks'), 
            Input('csv_remote', 'n_clicks')
        ]
)
def update_graph(json, csv_local, csv_remote):
    # print(x, y)
    # if g == 'Bar':
    #     fig = px.bar(df, x=x, y=y)
    # if g == 'Line':
    #     df1 = df.sort_values(by=y)
    #     fig = px.line(df1, x=x, y=y, markers=True)
    # if g == 'Histogram':
    #     fig = px.histogram(df, x=x, y=y, histfunc='avg')
    # if g == 'Scatter':
    #     fig = px.scatter(df, x=x, y=y)

    if(json!=None and json > selection_state[0]):
        selection_state[0] = json
        return graph_data_json
    if(csv_local!=None and csv_local > selection_state[1]):
        selection_state[1] = csv_local
        return graph_data_local
    if(csv_remote!=None and csv_remote > selection_state[2]):
        selection_state[2] = csv_remote
        return graph_data_remote
    return None


@callback( 
        Output('json-input', 'valid'),
        [
            Input('json-input', 'value'),
            Input('json-input', 'valid'),
        ]
)
def check_json_data(json_input, valid):
    # print(x, y)
    # if g == 'Bar':
    #     fig = px.bar(df, x=x, y=y)
    # if g == 'Line':
    #     df1 = df.sort_values(by=y)
    #     fig = px.line(df1, x=x, y=y, markers=True)
    # if g == 'Histogram':
    #     fig = px.histogram(df, x=x, y=y, histfunc='avg')
    # if g == 'Scatter':
    #     fig = px.scatter(df, x=x, y=y)
    # print(json_input)
    try:
        json.loads(json_input)
        return True
    except:
        return False
    return None



@callback( 
        Output('dummy-tag', 'value'),
        [
            Input('submit-button-json', 'n_clicks'), 
            Input('json-input', 'value'),
            Input('submit-button-local', 'n_clicks'), 
            Input('json-input', 'value'),
            Input('submit-button-remote', 'n_clicks'), 
            Input('json-input', 'value'),
        ]
)
def get_json_data(submit, json_input):
    # print(x, y)
    # if g == 'Bar':
    #     fig = px.bar(df, x=x, y=y)
    # if g == 'Line':
    #     df1 = df.sort_values(by=y)
    #     fig = px.line(df1, x=x, y=y, markers=True)
    # if g == 'Histogram':
    #     fig = px.histogram(df, x=x, y=y, histfunc='avg')
    # if g == 'Scatter':
    #     fig = px.scatter(df, x=x, y=y)

    if(submit):
        data = json.loads(json_input)
        df = pd.DataFrame.from_dict(data['data'])
        df.to_csv('static/file.csv', index=False)
    return None


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
])

items2 = [
    dbc.DropdownMenuItem("Experiment 1", id="json_format"),
    dbc.DropdownMenuItem(divider=True),
    dbc.DropdownMenuItem("Experiment 2", id="csv_local"),
    dbc.DropdownMenuItem(divider=True),
    dbc.DropdownMenuItem("Experiment", id="csv_remote"),
]

graph_page = html.Div([
    html.Div([
        html.Div([
            html.P('Graphical Representation', className='fs-3 fw-medium text-start text-primary col', style={
                'font-family': 'Arial',
            }),
            html.Div([
                dbc.DropdownMenu(
                    label="Experiment", children=items2, className='float-end',style={
                        'width': 'auto',
                        'justify-items':'end',
                        'justify-content':'flex-end',
                        'justify-self':'right'
                    }
                ),
            ], className='col justify-content-end'),
            html.Div([
                html.Div([
                    html.Div([
                        html.H6('X-axis data:'),
                    ]),
                    dcc.RadioItems(inline=True, labelStyle={
                        'margin-left': 10,
                        'padding-left': 5
                    }, id='x-axis-radio'),
                ], className='d-flex'),
                html.Div([
                    html.Div([
                        html.H6('Y-axis data:'),
                    ]),
                    dcc.RadioItems( inline=True, labelStyle={
                        'margin-left': 10,
                        'padding-left': 5
                    }, id='y-axis-radio'),
                ], className='d-flex'),
            ], className='d-flex flex-column', style={
                'gap':10
            })
        ], className="row py-2 px-4"),
        html.Div([
            html.Div([
                html.Div([
                    html.H6('Graphs:'),
                ]),
                dcc.RadioItems(['Line', 'Scatter', 'Bar'], 'Line', inline=False, labelStyle={
                    'margin-left': 10,
                    'padding-left': 5,
                    'margin-top':10
                }, id="graph-type"),
            ], className='d-flex flex-column'),
            html.Div([
                dcc.Graph(figure={}, id='graph')
            ], className='col ps-3', style={
                'border-left': '1px solid #7A7B7C',
            }),
        ],className='d-flex p-4', style={
            'gap':40
        })
    ], className='container min-vh-75 bg-light rounded-1')
], className='d-flex bg-secondary min-vh-100 min-vw-100 px-1 py-0 justify-content-center')

@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/graph-page':
        return graph_page
    return home_page_layout
    
@app.callback([
        Output('x-axis-radio', 'options'),
        Output('x-axis-radio', 'value'),
        Output('y-axis-radio', 'options'),
        Output('y-axis-radio', 'value'),
    ],[
        Input('url', 'pathname'),
    ])
def display_graph(pathname):
    if(pathname == '/graph-page'):
        table = pd.read_csv("static/file.csv")
        columns = table.columns
        selected_column_x = columns[0]
        selected_column_y = columns[1]
        # fig = px.line(table, x=selected_column_x, y=selected_column_y, markers=True)
        return columns, selected_column_x, columns, selected_column_y
    return None, None, None, None

@callback(
        Output(component_id='graph', component_property='figure'),
    [
        Input(component_id='graph-type', component_property='value'),
        Input('x-axis-radio', 'value'),
        Input('y-axis-radio', 'value'),
    ]
)
def change_graph_type(g, x, y):
    table = pd.read_csv("static/file.csv")
    if g == 'Bar':
        fig = px.bar(table, x=x, y=y)
    if g == 'Line':
        df1 = table.sort_values(by=y)
        fig = px.line(df1, x=x, y=y, markers=True)
    if g == 'Histogram':
        fig = px.histogram(table, x=x, y=y, histfunc='avg')
    if g == 'Scatter':
        fig = px.scatter(table, x=x, y=y)
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
