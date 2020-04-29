#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 11:34:12 2020

@author: francois
"""

import streamlit as st

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date, timedelta

import altair as alt

DATA_WORLD_CONFIRMED_GLOBAL = 'time_series_covid19_confirmed_global.csv'
DATA_WORLD_DEATHS_GLOBAL = 'time_series_covid19_deaths_global.csv'
DATA_WORLD_RECOVERED_GLOBAL = 'time_series_covid19_recovered_global.csv'

def _max_width_():
    max_width_str = f"max-width: 2000px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>    
    """,
        unsafe_allow_html=True,
    )
    
#_max_width_()

@st.cache()
def load_data():
    print('Cache update')
    
    df_world_confirmed = pd.read_csv(DATA_WORLD_CONFIRMED_GLOBAL, encoding='utf-8')
    df_world_deaths = pd.read_csv(DATA_WORLD_DEATHS_GLOBAL, encoding='utf-8')
    df_world_recovered = pd.read_csv(DATA_WORLD_RECOVERED_GLOBAL, encoding='utf-8')
    
    
    return(df_world_confirmed, df_world_deaths, df_world_recovered)

st.title('Coronavirus visualisation') 
st.header('François BOYER')
st.write('Dataset : https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series')

df_world_confirmed, df_world_deaths, df_world_recovered = load_data()

#st.write(df_world_confirmed.columns)

yesterday = date.today() - timedelta(days=1)
yesterday_colname = yesterday.strftime('%m/%d/%y').lstrip('0').replace("/0", "/")

#st.table(df_world_deaths)
st.write(yesterday_colname)

#st.table(df_world_deaths[yesterday_colname])

data_deaths = df_world_deaths[['Country/Region', yesterday_colname]].groupby('Country/Region').sum().sort_values(by='Country/Region')[yesterday_colname]
data_recovered = df_world_recovered[['Country/Region', yesterday_colname]].groupby('Country/Region').sum().sort_values(by='Country/Region')[yesterday_colname]
data_closed_cases = data_deaths + data_recovered
data_countries = df_world_deaths[['Country/Region', yesterday_colname]].groupby('Country/Region').sum().sort_values(by='Country/Region')


max_closed_cases = st.slider('Max number of death+recovered to display', min_value=0,\
                             max_value=data_closed_cases.max(),\
                             #value=data_closed_cases.max(),\
                             step=10)

st.write(max_closed_cases)

#max_closed_cases = data_closed_cases.max()
#print(max_closed_cases)

filtered_indexes = data_closed_cases[data_closed_cases <= max_closed_cases].index

data_deaths_filtered = data_deaths.loc[filtered_indexes]
data_recovered_filtered = data_recovered.loc[filtered_indexes]
data_closed_cases_filtered = data_closed_cases.loc[filtered_indexes]

data_countries_filtered = data_countries.loc[filtered_indexes]


################### Graph ###################################################


X_data = data_closed_cases_filtered
Y_data = data_deaths_filtered
labels_data = data_countries_filtered.index.tolist()

df_source = pd.DataFrame({
    'Number of deaths + recovered since start of crisis': X_data,
    'Number of deaths': Y_data,
    'label': labels_data
})


#chart = alt.Chart(df_source).mark_circle().encode(x='Number of deaths + recovered since start of crisis:Q', y='Number of deaths:Q')


chart = alt.Chart(df_source, width=1000, height=600).mark_circle().encode(x='Number of deaths + recovered since start of crisis:Q', \
                 y='Number of deaths:Q').properties(title=f'COVID19 World : Number of deaths / (Number of deaths + recovered) (updated {yesterday_colname})')


'''
chart = alt.Chart(df_source, width=1000, height=600).mark_circle().encode(alt.X('Number of deaths + recovered since start of crisis:Q', scale=alt.Scale(domain=(5, maxscale))), \
                 y='Number of deaths:Q').properties(title=f'COVID19 World : Number of deaths / (Number of deaths + recovered) (updated {yesterday_colname})')
'''

text = chart.mark_text(
    align='left',
    baseline='middle',
    dx=7
).encode(
    text='label'
)


st.altair_chart(chart + text, use_container_width=True)

'''
df = pd.DataFrame(np.random.randn(200, 3), columns=['a', 'b', 'c'])

c = alt.Chart(df).mark_circle().encode(x='a', y='b', size='c', color='c', tooltip=['a', 'b', 'c'])

st.altair_chart(c, use_container_width=True)
'''

#############################################################################


