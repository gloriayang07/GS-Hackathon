#!/usr/bin/env python
# coding: utf-8

# In[1]:


#setting up environment
import requests
import json

import datetime


from gs_quant.data import Dataset
from gs_quant.session import GsSession, Environment

import plotly.graph_objects as go
import numpy as np

import plotly.express as px
import plotly.graph_objects as go


client_id = r'e1f57f8843eb49bf9879ae4b1c31f80e'
client_secret = r'94770a526664211cf9805706d623f188721603bfa4668e98d58bbcbdbed96b56'

auth_data = {
            'grant_type'    : 'client_credentials',
                'client_id'     : client_id,
                    'client_secret' : client_secret,
                        'scope'         : 'read_content read_financial_data read_product_data read_user_profile'
                        }

# create session instance
session = requests.Session()

# make a POST to retrieve access_token
auth_request = session.post('https://idfs.gs.com/as/token.oauth2', data = auth_data)
access_token_dict = json.loads(auth_request.text)
access_token = access_token_dict['access_token']

# update session headers
session.headers.update({'Authorization':'Bearer '+ access_token})

# test API connectivity
request_url = 'https://api.marquee.gs.com/v1/users/self'
request = session.get(url=request_url)

GsSession.use(Environment.PROD, client_id, client_secret, ('read_product_data',))

##################################################################
##################################################################

#Extract Data
ds_who = Dataset('COVID19_COUNTRY_DAILY_WHO')
data_who = ds_who.get_data(datetime.date(2020, 1, 21), countryId=["US", "GB", "IN", "BR", "NG", "NZ"])


# In[37]:


##################################################################
##################################################################

#Line graph for percentages
countries = set(data_who['countryName'])

line_p = go.Figure()

x = data_who.index

for each in countries:
        y = data_who.loc[data_who['countryName'] == each]
            line_p.add_trace(go.Scatter(x=x, 
                                    y=((y['totalFatalities']/y['totalConfirmed'])*100),  
                                                        mode='lines',
                                                                            name=each,
                                                                                                line=dict( dash='dot'),
                                                                                                                    connectgaps=True,))
                

            y = data_who.groupby([data_who.index]).sum()
            line_p.add_trace(go.Scatter(x=x, 
                                    y=((y['totalFatalities']/y['totalConfirmed'])*100),  
                                                        mode='lines',
                                                                            name="Average"))

            line_p.update_xaxes(
                        rangeslider_visible=True,
                            rangeselector=dict(
                                        buttons=list([
                                                        dict(count=1, label="1m", step="month", stepmode="backward"),
                                                                    dict(count=6, label="6m", step="month", stepmode="backward"),
                                                                                dict(count=1, label="YTD", step="year", stepmode="todate"),
                                                                                            dict(count=1, label="1y", step="year", stepmode="backward"),
                                                                                                        dict(step="all")
                                                                                                                    ])
                                                ),
                                title="Date"
                                    )

            line_p.update_yaxes(
                        title="Percentage of Fatalities/Confirmed Cases"
                            )

            line_p.update_layout(
                        title="Total Fatalities as a Percentage of Total COVID-19 Cases"
                        )

            line_p.show()


            # In[33]:


            ##################################################################
            ##################################################################

            #Total cases by country
            who_group = data_who.groupby([data_who.index]).cumsum()

            bar = go.Figure()
            bar.add_trace(go.Histogram(histfunc="sum",
                                           x=data_who['countryName'], 
                                                                      y= data_who['newConfirmed'],
                                                                                                 name="Total Confirmed Cases"))
            bar.add_trace(go.Histogram(histfunc="sum",
                                           x=data_who['countryName'], 
                                                                      y= data_who['newFatalities'],
                                                                                                 name="Total Fatalities"))

            bar.update_layout(barmode='overlay')


            bar.update_traces(opacity=0.5)

            bar.update_layout(
                        title="Total Fatalities vs Total COVID-19 Cases by country"
                        )

            bar.update_xaxes(
                        title="Country"
                            )

            bar.update_yaxes(
                        title="Cumulative Amount"
                            )

            bar.show()


