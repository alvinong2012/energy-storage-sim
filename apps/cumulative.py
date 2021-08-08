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

# Connect to your app pages
#from apps import cumulative, split
from app import app

# get relative data folder



layout = dbc.Container([ 
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
@app.callback(
            [Output(component_id = 'NSW_cumulative', component_property = 'figure'),
            Output(component_id = 'QLD_cumulative', component_property = 'figure'),
            Output(component_id = 'VIC_cumulative', component_property = 'figure'),
            Output(component_id = 'TAS_cumulative', component_property = 'figure'),
            Output(component_id = 'SA_cumulative', component_property = 'figure')],
            [Input(component_id = 'storage_df', component_property='data')]
            )
def create_graph(storage_df):

   storage = pd.read_json(storage_df, orient='columns')

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

   return(NSW_cumulative, QLD_cumulative, VIC_cumulative, TAS_cumulative, SA_cumulative)