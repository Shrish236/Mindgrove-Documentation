# Import packages
import dash
from flask import Flask, request
from dash import Dash, html, dash_table, dcc, callback, Output, Input, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash_bootstrap_components as dbc
import json, base64, io
import csv


table = ""
data_format = ""
x_axis_options = []
y_axis_options = []
graph_list = []
df = pd.DataFrame()
# Incorporate data
# df = pd.read_csv('static/Employee.csv')

server = Flask(__name__)
# Initialize the app
app = Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP, 'static/styles.css'], suppress_callback_exceptions=True)

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
    # dbc.DropdownMenuItem("JSON Format", id="json_format"),
    # dbc.DropdownMenuItem(divider=True),
    dbc.DropdownMenuItem("Local CSV File", id="csv_local"),
    # dbc.DropdownMenuItem(divider=True),
    # dbc.DropdownMenuItem("Link to CSV File", id="csv_remote"),
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
], id='2')

graph_data_local = html.Div([
    html.P(
        "Upload your local csv file here",
        className="card-text",
    ),
    dcc.Upload(
        id='upload-local-csv',
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
], id='1', className='p-1')

graph_data_remote = html.Div([
    html.P(
        "Paste the link to remote CSV file here",
        className="card-text",
    ),
    dbc.Input(placeholder="Eg: https://www.drive.google.com/file", type="text", id='remote-link'),
    dbc.FormText("Make sure the file is given open access!", className='text-danger'),
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
                            label="Data Format", children=items, id='format-dropdown'
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
                                    {"label": "Scatter plot", "value": "Scatter"},
                                    {"label": "Line plot", "value": "Line"},
                                    {"label": "Bar graph", "value": "Bar"},
                                ],
                                label_checked_style={"color": "red"},
                                input_checked_style={
                                    "backgroundColor": "#fa7268",
                                    "borderColor": "#ea6258",
                                },
                            ),
                            html.P(id='dummy-tag2'),
                            html.P(id='dummy-tag3'),
                            dbc.Checklist(
                                id="checklist-selected-style1",
                                options=[
                                    {"label": "Histogram", "value": "Histogram"},
                                    {"label": "Pie chart", "value": "Pie"},
                                    {"label": "Distplot", "value": "Distplot"},
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
                                    id='data-format', className='p-1'),
                                    html.Div([
                                        dbc.Button("Upload Data", outline=True, color="primary", id='submit-button', ),
                                    ], className='d-flex justify-content-center p-2 pt-4'),
                                    
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
                html.P(id='dummy-tag1'),
            ], className='col px-4')
        ], className='row'),
        html.Div([
        ], className='row', id='columns-select'),
    ], className='container min-vh-75 bg-light rounded-1')
], className='d-flex bg-secondary min-vh-100 min-vw-100 px-3 py-5 justify-content-center')


# selection_state = [0, 0, 0]
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
            # Input(component_id='json_format', component_property='n_clicks'), 
            Input('csv_local', 'n_clicks'), 
            # Input('csv_remote', 'n_clicks')
        ]
)
def update_graph(csv_local):
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
    global data_format
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    # if('json_format' in  changed_id):
    #     data_format = "json"
    #     return graph_data_json
    if('csv_local' in changed_id):
        data_format = "local"
        return graph_data_local
    # elif('csv_remote' in changed_id):
    #     data_format = "remote"
    #     return graph_data_remote
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
        Output('dummy-tag3', 'value'),
        Input('checklist-selected-style', 'value'),
        Input('checklist-selected-style1', 'value'),
)
def update_graph_list(list1, list2):
    # print(list1, list2)
    global graph_list
    if list1 and len(list1)!=0:
        for i in list1:
            if i not in graph_list:
                graph_list.append(i)
    if list2 and len(list2)!=0:
        for i in list2:
            if i not in graph_list:
                graph_list.append(i)
    return None



# def parse_contents(contents, filename, date):
    
@callback( 
        Output('dummy-tag', 'value'),
        Input('submit-button', 'n_clicks'), 
        Input('json-input', 'value'),
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
    # print("hello")
    # print(submit_json, json_input, submit_local, submit_remote, remote_link, contents, filename, last_modified)
    if(submit and data_format == "json"):
        data = json.loads(json_input)
        # print(data['data'])
        for i, j in data['data'].items():
            print(i, j)
        # df = pd.DataFrame.from_dict(data['data'])
        # df.to_csv('static/file.csv', index=False)

    return None


local_file_uploaded = html.Div([
    "File uploaded successfully!",
], className="text-center font-italic")
file_not_uploaded=html.Div([
    'Drag and Drop or ',
    html.A('Select Files', className='fst-italic font-decoration-underline')
])

column_select_layout = html.Div([
    html.Hr(),
    html.Div([
        dbc.Card(
            [
                dbc.CardHeader("Column selection for graph representation"),
                dbc.CardBody(
                    [
                        html.H5("Select your x-axis and y-axis columns", className="card-title"),
                        html.Div([
                            html.Div([
                                html.P("X-axis", className="font-italic"),
                                dcc.Dropdown(
                                    multi=True, id='x-axis-select'
                                )
                            ], className='col text-center p-2 mr-2'),
                            html.Div([
                                html.P("Y-axis", className="font-italic"),
                                dcc.Dropdown(
                                    multi=True, id='y-axis-select'
                                )
                            ], className='col text-center p-2'),
                        ],id='k', className='d-flex justify-content-between p-3', style={
                            'justify-content':'space-between'
                        }),
                        html.Div([
                            dbc.Button("Submit", outline=True, color="primary", id='columns-submit', href='/graph-page'),
                        ], className='d-flex justify-content-center p-2 pt-4'),
                        html.P(id='dummy-tag-column-1')
                                    
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
    ], className='d-flex align-items-center'),
], className="px-5 py-3 text-center")
@callback(
    Output('upload-local-csv', 'children'),
    Output('columns-select', 'children'),
    Input('submit-button', 'n_clicks'),
    State('upload-local-csv', 'contents'),
    State('upload-local-csv', 'filename'),
    State('upload-local-csv', 'last_modified'),
)
def get_local_csv(submit, contents, filename, last_modified):
    if(submit and data_format=="local"):
        # print("hello")
        if filename is not None:
            # children = parse_contents(contents, filename, last_modified)
            content_type, content_string = contents.split(',')
            # define data frame as global
            decoded = base64.b64decode(content_string)
            global df
            try:
                if 'csv' in filename:
                    
                    # Assume that the user uploaded a CSV file
                    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                    # app.session['data'] = df
                    # print(df)
                    df.to_csv('static/file.csv', index=False)

                elif 'xls' in filename:
                    
                    # Assume that the user uploaded an Excel file
                    df = pd.read_excel(io.BytesIO(decoded))
                
                return local_file_uploaded, column_select_layout

            except Exception as e:
                print(e)
                return html.Div([
                    'There was an error processing this file.'
                ]), None, 

            
    return file_not_uploaded, None



@callback(
    Output('x-axis-select', 'options'),
    Output('y-axis-select', 'options'),
    Input('submit-button', 'n_clicks')
)
def update_column_select(submit):
    global df
    if(submit):
        return df.columns, df.columns

@callback(
        Output('dummy-tag-column-1', 'value'),
        Input('x-axis-select', 'value'),
        Input('y-axis-select', 'value'),
        Input('columns-select', 'n_clicks')
)
def set_columns(xaxis, yaxis, submit):
    global x_axis_options
    global y_axis_options
    if(submit):
        x_axis_options = xaxis
        y_axis_options = yaxis
    return None

@callback(
    Output('dummy-tag2', 'value'),
    Input('submit-button', 'n_clicks'),
    Input('remote-link', 'value'),
)
def get_remote_csv(submit, file):
    if(submit and data_format=="remote"):
        # print("hello")
        global df
        df = pd.read_csv(file)
        df.to_csv('static/file.csv', index=False)
    return None

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
])

graph_page = html.Div([
    html.Div([
        html.Div([
            html.P('Graphical Representation', className='fs-3 fw-medium text-start text-primary col', style={
                'font-family': 'Arial',
            }),
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
                dcc.RadioItems(graph_list, 'Line' if len(graph_list) == 0 else graph_list[0], inline=False, labelStyle={
                    'margin-left': 10,
                    'padding-left': 5,
                    'margin-top':10
                }, id="graph-type"),
                html.Div(
                    [
                        html.H6("Graph scale:"),
                        dbc.Checklist(
                            options=[
                                {"label": "Log scale", "value": 1},
                            ],
                            value=[1],
                            id="log-scale-switch",
                            switch=True,
                        ),
                    ],
                className='my-2'),
            ], className='d-flex flex-column'),
            html.Div([
                dcc.Graph(figure={}, id='graph')
            ], className='col ps-3', style={
                'border-left': '1px solid #7A7B7C',
                'width': 'inherit',
                'overflow-x':'auto'
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
        Output('graph-type', 'value')
    ],[
        Input('url', 'pathname'),
    ])
def display_graph(pathname):
    if(pathname == '/graph-page'):
        global df
        y_axis_options.insert(0, 'All')
        selected_column_x = x_axis_options[0]
        selected_column_y = y_axis_options[0]
        # fig = px.line(table, x=selected_column_x, y=selected_column_y, markers=True)
        return x_axis_options, selected_column_x, y_axis_options, selected_column_y, graph_list[0]
    return None, None, None, None

@callback(
        Output(component_id='graph', component_property='figure'),
    [
        Input(component_id='graph-type', component_property='value'),
        Input('x-axis-radio', 'value'),
        Input('y-axis-radio', 'value'),
        Input('log-scale-switch', 'value')
    ]
)
def change_graph_type(g, x, y, scale):
    table = pd.read_csv("static/file.csv")
    fig = go.Figure()
    global df
    global y_axis_options
    print(scale)
    # print(y_axis_options)
    if(y == 'All'):
        y = y_axis_options[1:]   
    if g == 'Bar':
        fig = px.bar(df, x=x, y=y, barmode='group')
    if g == 'Line':
        df1 = df.sort_values(by=y)
        fig = px.line(df1, x=x, y=y, markers=True)
    if g == 'Histogram':
        fig = px.histogram(df, x=x, y=y, histfunc='avg')
    if g == 'Scatter':
        fig = px.scatter(df, x=x, y=y)
    if g == 'Pie':
        fig = px.pie(df, values=y, names=x, hole=.2)
    if g == 'Distplot':
        # print(table[y])
        fig = ff.create_distplot([df[y].values.tolist()], ["data"])

    if(len(scale)!=0 and scale[0] == 1):
        fig.update_yaxes(type='log')
    elif(len(scale)==0):
        fig.update_yaxes(type='-')
    fig.update_layout(
        hovermode="x", 
        width=2500, 
        legend=dict(x=0, y=1.1, xanchor='left', 
        yanchor='top', 
        orientation='h', 
        title='Columns', 
        title_font_family="Times New Roman",
        font=dict(
            family="Courier",
            size=12,
            color="black",
        ),
        ))
    fig.update_layout(xaxis=dict(
        title='<b>Iterations</b>',
        titlefont=dict(
            family='Arial',
            size=14,
            color='black'
        )
    ))

    fig.update_layout(yaxis=dict(
        title='<b>Values</b>',
        titlefont=dict(
            family='Arial',
            size=14,
            color='black'
        )
    ))
    fig.for_each_trace(lambda t: t.update(name = '<b>' + t.name +'</b>'))
    return fig


@server.route('/post-json', methods=['POST'])
def req():
    print('Request triggered!')  # For debugging purposes, prints to console
    print(request.json)
    return "hbkb"

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
