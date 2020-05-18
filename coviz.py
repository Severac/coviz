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

import sys

import pydeck as pdk

import plotly.graph_objects as go

DATA_WORLD_CONFIRMED_GLOBAL = 'time_series_covid19_confirmed_global.csv'
DATA_WORLD_DEATHS_GLOBAL = 'time_series_covid19_deaths_global.csv'
DATA_WORLD_RECOVERED_GLOBAL = 'time_series_covid19_recovered_global.csv'

DATA_US_CONFIRMED_GLOBAL = 'time_series_covid19_confirmed_US.csv'
DATA_US_DEATHS_GLOBAL = 'time_series_covid19_deaths_US.csv'

# Lesotho, Saint Helena, comoros not in dataset : removed from list below
AFRICAN_COUNTRIES =  ["Nigeria","Ethiopia","Egypt","Congo (Brazzaville)","South Africa","Tanzania","Kenya","Uganda","Algeria","Sudan","Morocco","Angola","Ghana","Mozambique","Madagascar","Cameroon","Cote d'Ivoire","Niger","Burkina Faso","Mali","Malawi","Zambia","Senegal","Chad","Somalia","Zimbabwe","Guinea","Rwanda","Benin","Tunisia","Burundi","South Sudan","Togo","Sierra Leone","Libya","Congo (Kinshasa)","Liberia","Central African Republic","Mauritania","Eritrea","Namibia","Gambia","Botswana","Gabon","Guinea-Bissau","Equatorial Guinea","Mauritius","Eswatini","Djibouti","Western Sahara","Cabo Verde","Sao Tome and Principe","Seychelles"]

US_state_codes_dict = {'American Samoa' : 'AS', 'Guam': 'GU', 'Northern Mariana Islands' : 'MP',
    'Puerto Rico': 'PR', 'Virgin Islands': 'VI',
    'District of Columbia' : 'DC','Mississippi': 'MS', 'Oklahoma': 'OK', 
    'Delaware': 'DE', 'Minnesota': 'MN', 'Illinois': 'IL', 'Arkansas': 'AR', 
    'New Mexico': 'NM', 'Indiana': 'IN', 'Maryland': 'MD', 'Louisiana': 'LA', 
    'Idaho': 'ID', 'Wyoming': 'WY', 'Tennessee': 'TN', 'Arizona': 'AZ', 
    'Iowa': 'IA', 'Michigan': 'MI', 'Kansas': 'KS', 'Utah': 'UT', 
    'Virginia': 'VA', 'Oregon': 'OR', 'Connecticut': 'CT', 'Montana': 'MT', 
    'California': 'CA', 'Massachusetts': 'MA', 'West Virginia': 'WV', 
    'South Carolina': 'SC', 'New Hampshire': 'NH', 'Wisconsin': 'WI',
    'Vermont': 'VT', 'Georgia': 'GA', 'North Dakota': 'ND', 
    'Pennsylvania': 'PA', 'Florida': 'FL', 'Alaska': 'AK', 'Kentucky': 'KY', 
    'Hawaii': 'HI', 'Nebraska': 'NE', 'Missouri': 'MO', 'Ohio': 'OH', 
    'Alabama': 'AL', 'Rhode Island': 'RI', 'South Dakota': 'SD', 
    'Colorado': 'CO', 'New Jersey': 'NJ', 'Washington': 'WA', 
    'North Carolina': 'NC', 'New York': 'NY', 'Texas': 'TX', 
    'Nevada': 'NV', 'Maine': 'ME',
    'Diamond Princess' : 'NotUS',
    'Grand Princess' : 'NotUS',
    }


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
def load_data(date_colname):
    print('Cache update')
    
    import gc
    gc.collect()
    
    df_world_confirmed = pd.read_csv(DATA_WORLD_CONFIRMED_GLOBAL, encoding='utf-8')
    df_world_deaths = pd.read_csv(DATA_WORLD_DEATHS_GLOBAL, encoding='utf-8')
    df_world_recovered = pd.read_csv(DATA_WORLD_RECOVERED_GLOBAL, encoding='utf-8')
    
    df_us_confirmed = pd.read_csv(DATA_US_CONFIRMED_GLOBAL, encoding='utf-8')
    df_us_deaths = pd.read_csv(DATA_US_DEATHS_GLOBAL, encoding='utf-8')

    
    return(df_world_confirmed, df_world_deaths, df_world_recovered, df_us_confirmed, df_us_deaths)

st.title('Covid19 countries comparison') 

#st.write(df_world_confirmed.columns)

yesterday = date.today() - timedelta(days=1)
yesterday_colname = yesterday.strftime('%m/%d/%y').lstrip('0').replace("/0", "/")

df_world_confirmed, df_world_deaths, df_world_recovered, df_us_confirmed, df_us_deaths = load_data(yesterday_colname)

cnt = 0
while ((yesterday_colname not in df_world_deaths.columns.tolist()) and (cnt < 10)):
    yesterday = date.today() - timedelta(days=cnt+2)
    yesterday_colname = yesterday.strftime('%m/%d/%y').lstrip('0').replace("/0", "/")
    cnt += 1
    
    if (cnt >= 10):
        #st.error('Could not find data')
        sys.exit('Could not find data')


#st.table(df_world_deaths)
#st.write(yesterday_colname)

#st.table(df_world_deaths[yesterday_colname])

data_deaths = df_world_deaths[['Country/Region', yesterday_colname]].groupby('Country/Region').sum().sort_values(by='Country/Region')[yesterday_colname]
data_recovered = df_world_recovered[['Country/Region', yesterday_colname]].groupby('Country/Region').sum().sort_values(by='Country/Region')[yesterday_colname]
data_closed_cases = data_deaths + data_recovered
data_countries = df_world_deaths[['Country/Region', yesterday_colname]].groupby('Country/Region').sum().sort_values(by='Country/Region')

data_us_deaths = df_us_deaths[['Province_State', yesterday_colname]].groupby('Province_State').sum().sort_values(by='Province_State')[yesterday_colname]
data_us_confirmed = df_us_confirmed[['Province_State', yesterday_colname]].groupby('Province_State').sum().sort_values(by='Province_State')[yesterday_colname]
data_us_countries = df_us_deaths[['Province_State', yesterday_colname]].groupby('Province_State').sum().sort_values(by='Province_State')
data_us_pop = df_us_deaths[['Province_State', 'Population']].groupby('Province_State').sum().sort_values(by='Province_State')['Population']


countries_todisplay = st.selectbox('Countries to display', ['ALL', 'Africa', 'US'])

#max_closed_cases = data_closed_cases.max()
#print(max_closed_cases)


if (countries_todisplay == 'Africa') or (countries_todisplay == 'ALL'):
    if (countries_todisplay == 'Africa'):
        filtered_indexes = data_closed_cases.loc[AFRICAN_COUNTRIES].index
        
    elif (countries_todisplay == 'ALL'):
        #filtered_indexes = data_closed_cases[data_closed_cases <= max_closed_cases].index
        filtered_indexes = data_closed_cases.index
    
    
    data_deaths_filtered = data_deaths.loc[filtered_indexes]
    data_recovered_filtered = data_recovered.loc[filtered_indexes]
    data_closed_cases_filtered = data_closed_cases.loc[filtered_indexes]
    
    data_countries_filtered = data_countries.loc[filtered_indexes]
    
    #print(data_closed_cases_filtered.max())
    
    
    max_closed_cases = st.slider('Max number of death+recovered to display (decrease to see small data on the left)', min_value=0,\
                                 max_value=int(data_closed_cases_filtered.max()),\
                                 value=int(data_closed_cases_filtered.max()),\
                                 )
    

    
    log_scale_y = st.checkbox('Log scale Y', value=True)
    if (log_scale_y == True):
        log_scale_legend = ' (log scale)'
        
    else:
        log_scale_legend = '' 
    
    filtered_indexes = data_closed_cases_filtered[data_closed_cases_filtered <= max_closed_cases].index
    
    #if st.button('Show left side of the bar'):   
    #    filtered_indexes = data_closed_cases_filtered[data_closed_cases_filtered <= 100].index
    
    data_deaths_filtered = data_deaths_filtered.loc[filtered_indexes]
    data_recovered_filtered = data_recovered_filtered.loc[filtered_indexes]
    data_closed_cases_filtered = data_closed_cases_filtered.loc[filtered_indexes]
    
    data_countries_filtered = data_countries_filtered.loc[filtered_indexes]
    
    ## Input data for the graph :
    
    X_data = data_closed_cases_filtered
    Y_data = data_deaths_filtered
    labels_data = data_countries_filtered.index.tolist()
    
    graph_title = f"COVID19 : Number of deaths / (Number of deaths + recovered) (updated {yesterday_colname})"
    x_label_custom = "Number of deaths + recovered since start of crisis"
    y_label_custom = 'Number of deaths' + log_scale_legend
    y_label = 'Number of deaths'

elif (countries_todisplay == 'US'):
    max_confirmed_cases = st.slider('Max number of confirmed cases to display (decrease to see small data on the left)', min_value=0,\
                                 max_value=int(data_us_confirmed.max()),\
                                 value=int(data_us_confirmed.max()),\
                                 step=10)   
 
    log_scale_y = st.checkbox('Log scale Y', value=True)
    if (log_scale_y == True):
        log_scale_legend = ' (log scale)'
        
    else:
        log_scale_legend = ''
    
    filtered_indexes = data_us_confirmed[data_us_confirmed <= max_confirmed_cases].index
    
    data_us_deaths_filtered = data_us_deaths.loc[filtered_indexes]
    data_us_confirmed_filtered = data_us_confirmed.loc[filtered_indexes]
    
    data_us_countries_filtered = data_us_countries.loc[filtered_indexes]    
    data_us_pop_filtered = data_us_pop.loc[filtered_indexes]    
    
    ## Input data for the graph :
    X_data = data_us_confirmed_filtered
    Y_data = data_us_deaths_filtered
    labels_data = data_us_countries_filtered.index.tolist()    
    
    graph_title = f"COVID19 US : Number of deaths / Confirmed cases (updated {yesterday_colname})"
    x_label_custom = "Number of confirmed cases since start of crisis"
    y_label_custom = 'Number of deaths' + log_scale_legend
    y_label = 'Number of deaths'

################### Graph ###################################################

#st.write(labels_data)

#plt.figure(figsize=(32, 20))
plt.figure(figsize=(15, 9))
#plt.figure()

#plt.title(f"COVID19 World : Number of deaths / (Number of deaths + recovered) (updated {yesterday_colname})", fontsize=25)
plt.title(graph_title)
# Set x-axis label

ax = sns.regplot(x=X_data, y=Y_data, ci=99.9, truncate=False)
#ax.set(xscale='log', yscale='log')
#ax.set(xscale='log')
if (log_scale_y == True):
    ax.set(yscale='log')

closedcasescount_80p = X_data.sum() * 0.80
min_value_80p = X_data.loc[X_data[X_data.sort_values(ascending=False).cumsum() <= closedcasescount_80p].index].min()

ax.set(xlabel=x_label_custom, ylabel=y_label_custom)

#ax.set_xlim(0, 5000)
#ax.set_ylim(0, 300)

plt.axvline(min_value_80p, color='green', linestyle='--', label=f"80% of deaths+recovered are at the right of the line ({closedcasescount_80p:.0f} people)")
plt.legend()

for i, txt in enumerate(labels_data):
    #if (X_data[i] > X_data.max() * 0.20) or (txt == 'Guinea'):
        #ax.annotate(txt, (X_data[i], Y_data[i]), xytext=(X_data[i] + 0.1, Y_data[i]))      
        #print('!')
        ax.annotate(txt, (X_data[i], Y_data[i]), xytext=(X_data[i] + 1, Y_data[i]))      
        
ax.annotate('François BOYER\nSource : John Hopkins University', xy=(1, 0), xytext=(-15, 10), fontsize=10,
    xycoords='axes fraction', textcoords='offset points',
    bbox=dict(facecolor='white', alpha=0.8),
    horizontalalignment='right', verticalalignment='bottom')



#plt.savefig('covid19-world-regplot-'+str(1)+'.png')
st.pyplot()

#############################################################################

st.write('NB : UK data is inaccurate because some "recovered" data is missing')


##### Display data and maps ##################################################

death_ratio = Y_data / X_data

df_map = pd.DataFrame(
    df_world_deaths[['4/25/20', 'Lat', 'Long']],
    columns=['4/25/20', 'Lat', 'Long'])

df_map.columns = ['4/25/20', 'lat', 'lon']

if (countries_todisplay == 'US'):
    locationmode_to_use = 'USA-states'
    z_data = (Y_data / X_data).fillna(0).astype(float)
    locations_to_use = [US_state_codes_dict[k] for k in Y_data.index.values]
    
else:
    locationmode_to_use = 'country names'
    z_data = (Y_data / X_data).fillna(0).astype(float)
    locations_to_use = Y_data.index.values
  
data = [dict(type = 'choropleth',
        colorscale = 'Reds',
        locations=locations_to_use, # 2 letters state code names
        z = z_data, # Data to be color-coded
        text = Y_data.index.values,
        locationmode = locationmode_to_use, # set of locations match entries in `locations
        colorbar = {'title':"Death ratio"},
       )]

layout = dict(title = f'{y_label} / {x_label_custom}',
              geo = dict(scope='world', showlakes = True)) #  if scope = 'usa', limit map scope to USA)

choromap = go.Figure(data = data, layout=layout)
    
st.write(choromap)

if (countries_todisplay == 'US'):
    Y_data = data_us_confirmed_filtered / data_us_pop_filtered # Does not work
    
    data = [dict(type = 'choropleth',
            colorscale = 'Reds',
            locations=[US_state_codes_dict[k] for k in Y_data.index.values], # 2 letters state code names
            z = Y_data, # Data to be color-coded
            text = Y_data.index.values,
            locationmode = locationmode_to_use, # set of locations match entries in `locations
            colorbar = {'title':"Confirmed cases ratio"},
           )]
    
    layout = dict(title = f'Confirmed cases / population',
                  geo = dict(scope='world', showlakes = True)) #  if scope = 'usa', limit map scope to USA)
    
    choromap2 = go.Figure(data = data, layout=layout)        

    st.write(choromap2)

display_data = st.checkbox('Display numerical data', value=True)

if (display_data == True):
    df_data_to_display = pd.concat([X_data, Y_data, death_ratio], axis=1)
    df_data_to_display.columns = [x_label_custom, y_label, 'Death ratio']
    
    st.dataframe(df_data_to_display)
    
    

st.write('François BOYER')
st.write('Dataset : https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series')

import gc
gc.collect()