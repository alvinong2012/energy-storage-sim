from dash.development.base_component import Component
import pandas as pd
import numpy as np
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import dash_table
from os import listdir
from os.path import isfile, join

# Connect to your app pages
#from apps import cumulative, split
from app import app

# ---------- Importing Inputs and Results


mypath = r'C:\Users\alvin\Desktop\University\Year 4 Term 2\Thesis\Thesis B\Simulation\Actual\Results'
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
filename_type = []
for y in onlyfiles:
    y = y.replace(' - Inputs.json', "")
    y = y.replace(' - Results.json', "")
    filename_type.append(y)
filename_type = list(set(filename_type))
print(filename_type)
filename_type1 = filename_type[0]

simulation_type = filename_type1
input_filename_x = simulation_type + ' - Inputs.json'
input_filename = join(mypath,input_filename_x)
inputs = pd.read_json (input_filename)
inputs =inputs.T
inputs = inputs.reset_index()

# ------------------------------------------------------------------------------
# App layout
app.layout = dbc.Container([
    
    dbc.Row([
        dbc.Col(html.H1('Energy Storage Simulation',
            className='text-center text-primary mb-4'),
            width = 12),
        dcc.Store(id='storage_df')    
    ]),
    dbc.Row(
        dbc.Col([dcc.Dropdown(
        id='simulation_select',
        options=[
            {'label': i, 'value': i} for i in filename_type],
            value = filename_type1)
        ],width = 6),justify = 'center'),

    html.Br(),

    dbc.Row([
        dash_table.DataTable(
            id = 'stor_info',
            columns=[{"name": i, "id": i} for i in inputs.columns],
            data=inputs.to_dict('records')
            )
    ], justify = 'center'),

    # dbc.Row([
    #     dcc.Location(id='url', refresh=False),
    #     html.Div([
    #         dcc.Link('Cumulative Graphs|', href='/apps/cumulative'),
    #         dcc.Link('Split Graphs', href='/apps/split'),
    #     ], className="row"),
    #     dbc.Col(id='page-content', children=[], width = 12)
    # ], justify = 'center'),  
    dbc.Row([
         dbc.Col([html.H4('New South Wales Cumulative Graph',className='text-center text-info my-4 mb-4'),
            dcc.Graph(id = 'NSW_cumulative')
         ])
     ], justify = 'center'), 
     
     dbc.Row([
         dbc.Col([html.H4('Queensland Cumulative Graph',className='text-center text-info mb-4'),
            dcc.Graph(id = 'QLD_cumulative')
         ])
     ], justify = 'center'),  
     dbc.Row([
         dbc.Col([html.H4('Victoria Cumulative Graph',className='text-center text-info mb-4'),
            dcc.Graph(id = 'VIC_cumulative')
         ])
     ], justify = 'center'),
     dbc.Row([
         dbc.Col([html.H4('Tasmania Cumulative Graph',className='text-center text-info mb-4'),
            dcc.Graph(id = 'TAS_cumulative')
         ])
     ], justify = 'center'),
     dbc.Row([
         dbc.Col([html.H4('South Australia Cumulative Graph',className='text-center text-info mb-4'),
            dcc.Graph(id = 'SA_cumulative')
         ])
     ], justify = 'center'),    
], fluid = True)


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
# @app.callback(Output(component_id='storage_df', component_property = 'data'),
#             Input('results', 'data'))


@app.callback([#Output('page-content', 'children'),
                #Output(component_id='storage_df', component_property = 'data'),
                Output(component_id='stor_info', component_property = 'data'),
                Output(component_id = 'NSW_cumulative', component_property = 'figure'),
                Output(component_id = 'QLD_cumulative', component_property = 'figure'),
                Output(component_id = 'VIC_cumulative', component_property = 'figure'),
                Output(component_id = 'TAS_cumulative', component_property = 'figure'),
                Output(component_id = 'SA_cumulative', component_property = 'figure')
                ],
              [Input('simulation_select','value')
              #Input('url', 'pathname')
              ])

def display_page(simulation_type):

    if simulation_type != None:

        result_filename_x = simulation_type + ' - Results.json'
        input_filename_x = simulation_type + ' - Inputs.json'
        result_filename = join(mypath, result_filename_x)
        input_filename = join(mypath,input_filename_x)
        inputs = pd.read_json (input_filename)
        inputs =inputs.T
        inputs = inputs.reset_index()
        results = pd.read_json (result_filename)
        #results = results_df.to_json(orient='columns')
    print(str(simulation_type))

    storage = results.copy()
    #NSW
    NSW_storage = storage.iloc[:,0:5]
    NSW_storage = NSW_storage.iloc[:, ::-1]
    NSW_cumulative = px.area(NSW_storage)
    
    #QLD
    QLD_storage = storage.iloc[:,6:11]
    QLD_storage = QLD_storage.iloc[:, ::-1]
    QLD_cumulative = px.area(QLD_storage)

    #VIC
    VIC_storage = storage.iloc[:,12:17]
    VIC_storage = VIC_storage.iloc[:, ::-1]
    VIC_cumulative = px.area(VIC_storage)

    #TAS
    TAS_storage = storage.iloc[:,18:23]
    TAS_storage = TAS_storage.iloc[:, ::-1]
    TAS_cumulative = px.area(TAS_storage)

    #SA
    SA_storage = storage.iloc[:,24:29]
    SA_storage = SA_storage.iloc[:, ::-1]
    SA_cumulative = px.area(SA_storage)


    #input_col = [{"name": i, "id": i} for i in inputs.columns]
    data = inputs.to_dict('records')
    # if pathname == '/apps/cumulative':
    #     x = cumulative.layout
    # # elif pathname == '/apps/split':
    # #     x= split.layout
    # else:
    #     x= "404 Page Error! Please choose a link"   
    
    return (data, NSW_cumulative, QLD_cumulative, VIC_cumulative, TAS_cumulative, SA_cumulative)#, input_col)
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True, port = 3000)


