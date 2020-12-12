#!/usr/bin/env python
# coding: utf-8

# In[1]:


from gs_quant.session import GsSession, Environment
from gs_quant.data import Dataset
from datetime import date
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import pandas as pd


# In[2]:


GsSession.use(client_id='8870cdcf26db4484beeef2b2166e1f15', 
              client_secret='9433b571fcf68a2fd73f7510b53e508518fd282b7fc65b43c7c9eda39410c8f7')


# In[3]:


who_dataset = Dataset('COVID19_COUNTRY_DAILY_WHO')


# In[4]:


def getDataSet(countryId):
    data_frame = who_dataset.get_data(countryId=countryId, start = date(2019,1,1))
    for i in range(1, len(data_frame)):
        data_frame['rateOfChange'] = (data_frame['newConfirmed'] - data_frame['newConfirmed'].shift())/data_frame['newConfirmed'].shift()
    data_frame['rateOfChange'] = data_frame['rateOfChange'].fillna(0)
    return data_frame


# In[5]:


data_frame_US = getDataSet('US')
data_frame_UK = getDataSet('GB')
data_frame_BR = getDataSet('BR')
data_frame_NG = getDataSet('NG')
data_frame_NZ = getDataSet('NZ')
data_frame_IN = getDataSet('IN')


# In[6]:


df=pd.concat([data_frame_US,data_frame_UK,data_frame_IN,data_frame_BR,data_frame_NG,data_frame_NZ])


# In[7]:


for country in df['countryId'].unique():
    fig = px.line(df[df['countryId']==country], y='rateOfChange', title=country)
    fig.show()


# In[8]:


fig = px.line(df, y='rateOfChange', color='countryId')

fig.show()

