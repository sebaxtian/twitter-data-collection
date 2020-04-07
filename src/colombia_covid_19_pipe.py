# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
#import geopandas as gpd # geodata processing
# Get geolocation using geocoder
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent='covid19co', timeout=None)
# Https requests
import requests
import unidecode
# Dates
from datetime import date
from calendar import day_name, month_name

# Short ID
import subprocess
import sys
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
try:
    from shortid import ShortId
except Exception:
    install('shortid')
    from shortid import ShortId

# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# Any results you write to the current directory are saved as output.

# %% [markdown]
# # Colombia Covid 19 Pipeline
# Dataset is obtained from [Instituto Nacional de Salud](https://www.ins.gov.co/Noticias/Paginas/Coronavirus.aspx) daily report Coronavirus 2019 from Colombia.
# 
# You can get the official dataset here: 
# [INS - Official Report](https://e.infogram.com/api/live/flex/bc384047-e71c-47d9-b606-1eb6a29962e3/664bc407-2569-4ab8-b7fb-9deb668ddb7a)
# 
# The number of new cases are increasing day by day around the world.
# This dataset has information about reported cases from 32 Colombia departments.
# 
# You can view and collaborate to the analysis here:
# [colombia_covid_19_analysis](https://www.kaggle.com/sebaxtian/colombia-covid-19-analysis) Kaggle Notebook Kernel.
# %% [markdown]
# ---

# %%
# Constants
INPUT_DIR = '/kaggle/input'
# Any results you write to the current directory are saved as output.
OUTPUT_DIR = './output'
# URL original dataset
URL_DATASET = 'https://e.infogram.com/api/live/flex/bc384047-e71c-47d9-b606-1eb6a29962e3/664bc407-2569-4ab8-b7fb-9deb668ddb7a'


# %%
# Reading the json as a dict
with requests.get(URL_DATASET) as original_dataset:
    data = original_dataset.json()
#print(data)

# Get attributes and data
attrs = data['data'][0][0]
del data['data'][0][0]
data = data['data'][0]

# Build dataframe
covid_df = pd.DataFrame(data=data, columns=attrs)

# Size dataframe
covid_df.shape


# %%
# Show dataframe
covid_df.tail()


# %%
# Rename columns
covid_df.rename(columns={
    "ID de caso": "id_case",
    "Fecha de diagnóstico": "date",
    "Ciudad de ubicación": "city",
    "Departamento o Distrito": "dept_dist",
    "Atención**": "care",
    "Edad": "age",
    "Sexo": "sex",
    "Tipo*": "kind",
    "País de procedencia": "country_origin"}, inplace=True)
# Show dataframe
covid_df.head()


# %%
# Clean empty rows
covid_df = covid_df[(covid_df['id_case'] != '') | (covid_df['date'] != '')]
# Show dataframe
covid_df.tail()


# %%
# Remove accents
covid_df['city'] = covid_df['city'].transform(lambda value: unidecode.unidecode(value))
covid_df['dept_dist'] = covid_df['dept_dist'].transform(lambda value: unidecode.unidecode(value))
# Show dataframe
covid_df.head()


# %%
# Add Day, Month, Year, Month Name and Day Name
covid_df['day'] = covid_df['date'].transform(lambda value: value.split('/')[0])
covid_df['month'] = covid_df['date'].transform(lambda value: value.split('/')[1])
covid_df['year'] = covid_df['date'].transform(lambda value: value.split('/')[2])
# English
#covid_df['month_name'] = covid_df['month'].transform(lambda value: month_name[int(value)])
#covid_df['day_name'] = covid_df['date'].transform(lambda value: day_name[date(int(value.split('/')[2]), int(value.split('/')[1]), int(value.split('/')[0])).weekday()])
# Spanish
nombre_mes = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
nombre_dia = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
covid_df['month_name'] = covid_df['month'].transform(lambda value: nombre_mes[int(value) - 1])
covid_df['day_name'] = covid_df['date'].transform(lambda value: nombre_dia[date(int(value.split('/')[2]), int(value.split('/')[1]), int(value.split('/')[0])).weekday()])
# Show dataframe
covid_df.head()


# %%
# Update Case ID
covid_df['id_case'] = covid_df['id_case'].transform(lambda value: ShortId().generate())
covid_df['id_case'] = covid_df['sex'] + covid_df['id_case'] + covid_df['age']
covid_df.head()


# %%
# Sort columns
covid_df = covid_df[['id_case', 'date', 'day', 'month', 'year', 'month_name', 'day_name', 'city', 'dept_dist', 'age', 'sex', 'kind', 'country_origin', 'care']]
covid_df.head()

# %% [markdown]
# ## Covid 19 Dataset
# > ***Output file***: covid19_co.csv

# %%
# Save dataframe
covid_df.to_csv(os.path.join(OUTPUT_DIR, 'covid19_co.csv'), index=False)

# %% [markdown]
# ---

# %%
# Cases by Date
covid_df_by_date = covid_df.groupby('date')['date'].count()
covid_df_by_date = pd.DataFrame(data={'date': covid_df_by_date.index, 'total': covid_df_by_date.values}, columns=['date', 'total'])
covid_df_by_date['date_iso'] = pd.to_datetime(covid_df_by_date['date'], format='%d/%m/%Y')
covid_df_by_date = covid_df_by_date.sort_values(by=['date_iso'], ascending=True)
covid_df_by_date['cumsum'] = covid_df_by_date['total'].cumsum()
covid_df_by_date = covid_df_by_date.drop(columns=['date_iso'])
covid_df_by_date.reset_index(inplace=True, drop=True)
# Show dataframe
covid_df_by_date.tail()

# %% [markdown]
# ## Cases by Date
# > ***Output file***: covid_19_by_date.csv

# %%
# Save dataframe
covid_df_by_date.to_csv(os.path.join(OUTPUT_DIR, 'covid_19_by_date.csv'), index=False)

# %% [markdown]
# ---

# %%
# Cases by Care
covid_df_by_care = covid_df.groupby('care')['care'].count().sort_values(ascending=False)
covid_df_by_care = pd.DataFrame(data={'care': covid_df_by_care.index, 'total': covid_df_by_care.values}, columns=['care', 'total'])
# Show dataframe
covid_df_by_care.head()

# %% [markdown]
# ## Cases by Care
# > ***Output file***: covid_19_by_care.csv

# %%
# Save dataframe
covid_df_by_care.to_csv(os.path.join(OUTPUT_DIR, 'covid_19_by_care.csv'), index=False)

# %% [markdown]
# ---

# %%
# Cases by Sex
covid_df_by_sex = covid_df.groupby('sex')['sex'].count().sort_values(ascending=False)
covid_df_by_sex = pd.DataFrame(data={'sex': covid_df_by_sex.index, 'total': covid_df_by_sex.values}, columns=['sex', 'total'])
# Show dataframe
covid_df_by_sex.head()

# %% [markdown]
# ## Cases by Sex
# > ***Output file***: covid_19_by_sex.csv

# %%
# Save dataframe
covid_df_by_sex.to_csv(os.path.join(OUTPUT_DIR, 'covid_19_by_sex.csv'), index=False)

# %% [markdown]
# ---

# %%
# Cases by Age
covid_df_by_age = covid_df.groupby('age')['age'].count().sort_values(ascending=False)
covid_df_by_age = pd.DataFrame(data={'age': covid_df_by_age.index, 'total': covid_df_by_age.values}, columns=['age', 'total'])
# Show dataframe
covid_df_by_age.head()

# %% [markdown]
# ## Cases by Age
# > ***Output file***: covid_19_by_age.csv

# %%
# Save dataframe
covid_df_by_age.to_csv(os.path.join(OUTPUT_DIR, 'covid_19_by_age.csv'), index=False)

# %% [markdown]
# ---

# %%
# Cases by Age and Sex
covid_df_by_age_sex = covid_df.groupby(['age', 'sex'])['id_case'].count().sort_values(ascending=False)
covid_df_by_age_sex = pd.DataFrame(data={'age': covid_df_by_age_sex.index.get_level_values('age'), 'sex': covid_df_by_age_sex.index.get_level_values('sex'), 'total': covid_df_by_age_sex.values}, columns=['age', 'sex', 'total'])
# Show dataframe
covid_df_by_age_sex.head()

# %% [markdown]
# ## Cases by Age and Sex
# > ***Output file***: covid_19_by_age_sex.csv

# %%
# Save dataframe
covid_df_by_age_sex.to_csv(os.path.join(OUTPUT_DIR, 'covid_19_by_age_sex.csv'), index=False)

# %% [markdown]
# ---

# %%
# Build dataframe by Age and Sex using intervals
def age_sex_intervals(dataframe):
    intervals = []
    i = 0
    while i < 100:
        interval_i = dataframe[(dataframe['age'] >= i) & (dataframe['age'] < i+10)]
        interval_i = interval_i.groupby('sex')['total'].sum().sort_values(ascending=False)
        if len(interval_i.values) > 0:
            interval_i = pd.DataFrame(data={'age': [ str(i) + '-' + str(i+9), str(i) + '-' + str(i+9)], 'sex': interval_i.index, 'total': interval_i.values}, columns=['age', 'sex', 'total'])
            intervals.append(interval_i)
        i = i + 10
    return pd.concat(intervals).reset_index(drop=True)
# Cases by Age and Sex using intervals
covid_df_by_age_sex_interval = covid_df_by_age_sex
covid_df_by_age_sex_interval['age'] = pd.to_numeric(covid_df_by_age_sex_interval['age'])
covid_df_by_age_sex_interval = age_sex_intervals(covid_df_by_age_sex_interval)
# Show dataframe
covid_df_by_age_sex_interval.head()

# %% [markdown]
# ## Cases by Age and Sex Interval
# > ***Output file***: covid_19_by_age_sex_interval.csv

# %%
# Save dataframe
covid_df_by_age_sex_interval.to_csv(os.path.join(OUTPUT_DIR, 'covid_19_by_age_sex_interval.csv'), index=False)

# %% [markdown]
# ---

# %%
# Cases by City
covid_df_by_city = covid_df.groupby('city')['city'].count().sort_values(ascending=False)
covid_df_by_city = pd.DataFrame(data={'city': covid_df_by_city.index, 'total': covid_df_by_city.values}, columns=['city', 'total'])
# Show dataframe
covid_df_by_city.head()


# %%
# Find city geolocation
def findgeopoint(city):
    geo = geolocator.geocode(city + ', Colombia')
    if geo:
        return geo.point
    else:
        return geolocator.geocode('Colombia').point


# %%
# Add city geolocation
covid_df_by_city['geo'] = covid_df_by_city['city'].transform(lambda value: findgeopoint(value))
# Add city latitude and longitude
covid_df_by_city['lat'] = covid_df_by_city['geo'].transform(lambda value: value.latitude)
covid_df_by_city['lng'] = covid_df_by_city['geo'].transform(lambda value: value.longitude)
covid_df_by_city = covid_df_by_city.drop(columns=['geo'])
# Show dataframe
covid_df_by_city.head()

# %% [markdown]
# ## Cases by City
# > ***Output file***: covid_19_by_city.csv

# %%
# Save dataframe
covid_df_by_city.to_csv(os.path.join(OUTPUT_DIR, 'covid_19_by_city.csv'), index=False)

# %% [markdown]
# ---

# %%
# Cases by Department or District
covid_df_by_dept_dist = covid_df.groupby('dept_dist')['dept_dist'].count().sort_values(ascending=False)
covid_df_by_dept_dist = pd.DataFrame(data={'dept_dist': covid_df_by_dept_dist.index, 'total': covid_df_by_dept_dist.values}, columns=['dept_dist', 'total'])
# Show dataframe
covid_df_by_dept_dist.head()


# %%
# Add dept_dist geolocation
covid_df_by_dept_dist['geo'] = covid_df_by_dept_dist['dept_dist'].transform(lambda value: findgeopoint(value))
# Add city latitude and longitude
covid_df_by_dept_dist['lat'] = covid_df_by_dept_dist['geo'].transform(lambda value: value.latitude)
covid_df_by_dept_dist['lng'] = covid_df_by_dept_dist['geo'].transform(lambda value: value.longitude)
covid_df_by_dept_dist = covid_df_by_dept_dist.drop(columns=['geo'])
# Show dataframe
covid_df_by_dept_dist.head()

# %% [markdown]
# ## Cases by Department or District
# > ***Output file***: covid_19_by_dept_dist.csv

# %%
# Save dataframe
covid_df_by_dept_dist.to_csv(os.path.join(OUTPUT_DIR, 'covid_19_by_dept_dist.csv'), index=False)

# %% [markdown]
# ---

# %%
# Cases by Care by Date
list_care = list(set(covid_df['care'].values))
print('list_care', list_care)
cases_by_care_by_date = []
# Each Care
for care in list_care:
    covid_df_care_by_date = covid_df[covid_df['care'] == care]
    covid_df_care_by_date = covid_df_care_by_date.groupby('date')['date'].count()
    covid_df_care_by_date = pd.DataFrame(data={'date': covid_df_care_by_date.index, 'care': ([care] * len(covid_df_care_by_date.index)), 'total': covid_df_care_by_date.values}, columns=['date', 'care', 'total'])
    covid_df_care_by_date['date_iso'] = pd.to_datetime(covid_df_care_by_date['date'], format='%d/%m/%Y')
    covid_df_care_by_date = covid_df_care_by_date.sort_values(by=['date_iso'], ascending=True)
    covid_df_care_by_date['cumsum'] = covid_df_care_by_date['total'].cumsum()
    covid_df_care_by_date = covid_df_care_by_date.drop(columns=['date_iso'])
    covid_df_care_by_date.reset_index(inplace=True, drop=True)
    cases_by_care_by_date.append(covid_df_care_by_date)
# Show dataframe
for i, care in enumerate(list_care):
    print(care, '\n', cases_by_care_by_date[i].tail())

# %% [markdown]
# ## Cases by Care by Date
# > ***Output files***: cases_by_care_by_date_(int).csv

# %%
# Save dataframe
for i, care in enumerate(list_care):
    cases_by_care_by_date[i].to_csv(os.path.join(OUTPUT_DIR, 'cases_by_care_by_date_' + str(i) + '.csv'), index=False)

# %% [markdown]
# ---

# %%
# Cases by Country Origin
covid_df_by_country_origin = covid_df.groupby('country_origin')['country_origin'].count().sort_values(ascending=False)
covid_df_by_country_origin = pd.DataFrame(data={'country_origin': covid_df_by_country_origin.index, 'total': covid_df_by_country_origin.values}, columns=['country_origin', 'total'])
# Show dataframe
covid_df_by_country_origin.head()

# %% [markdown]
# ## Cases by Country Origin
# > ***Output file***: covid_19_by_country_origin.csv

# %%
# Save dataframe
covid_df_by_country_origin.to_csv(os.path.join(OUTPUT_DIR, 'covid_19_by_country_origin.csv'), index=False)

# %% [markdown]
# ---

# %%
# Cases by Kind
covid_df_by_kind = covid_df.groupby('kind')['kind'].count().sort_values(ascending=False)
covid_df_by_kind = pd.DataFrame(data={'kind': covid_df_by_kind.index, 'total': covid_df_by_kind.values}, columns=['kind', 'total'])
# Show dataframe
covid_df_by_kind.head()

# %% [markdown]
# ## Cases by Kind
# > ***Output file***: covid_19_by_kind.csv

# %%
# Save dataframe
covid_df_by_kind.to_csv(os.path.join(OUTPUT_DIR, 'covid_19_by_kind.csv'), index=False)

# %% [markdown]
# ---

# %%
# Descarted Cases
# Reading the json as a dict
with requests.get('https://infogram.com/api/live/flex/5eb73bf0-6714-4bac-87cc-9ef0613bf697/c9a25571-e7c5-43c6-a7ac-d834a3b5e872?') as original_dataset:
    data = original_dataset.json()
#print(data['data'][0][3][0])

# Get attributes and data
attrs = data['data'][0][3][0]
del data
#print(attrs)
descarted_cases = attrs.split('<b>')[1].split('</b>')[0].replace('.', '')
print(descarted_cases)

# %% [markdown]
# ---

# %%
# Samples Processed
# Reading the json as a dict
with requests.get('https://infogram.com/api/live/flex/bc384047-e71c-47d9-b606-1eb6a29962e3/523ca417-2781-47f0-87e8-1ccc2d5c2839?') as original_dataset:
    data = original_dataset.json()
#print(data['data'][1])

# Get attributes and data
attrs = data['data'][1][0]
attrs[0] = 'Periodo'
del data['data'][1][0]
#print(attrs)
data = data['data'][1]
#print(data)

# Build dataframe
covid_df_samples_processed = pd.DataFrame(data=data, columns=attrs)

# Size dataframe
covid_df_samples_processed.head()


# %%
# Rename columns
covid_df_samples_processed.rename(columns={
    "Periodo": "period",
    "Muestras procesadas": "total_samples",
    "Acumulado procesadas": "accum_samples"}, inplace=True)
# Show dataframe
covid_df_samples_processed.head()


# %%
# Update date format
def update_date_format(period):
    date1 = period.split('-')[0]
    date2 = period.split('-')[1]
    if date1.split('/')[-1] == '20':
        date1 = '/'.join(date1.split('/')[0:-1]) + '/2020'
    if date2.split('/')[-1] == '20':
        date2 = '/'.join(date2.split('/')[0:-1]) + '/2020'
    return date1 + '-' + date2
# Example
#update_date_format('02/03/20-08/03/20')
# Update date format
covid_df_samples_processed['period'] = covid_df_samples_processed['period'].transform(lambda value: update_date_format(value))
# Show dataframe
covid_df_samples_processed.head()

# %% [markdown]
# ## Samples Processed
# > ***Output file***: covid_19_samples_processed.csv

# %%
# Save dataframe
covid_df_samples_processed.to_csv(os.path.join(OUTPUT_DIR, 'covid_19_samples_processed.csv'), index=False)

# %% [markdown]
# ---

# %%
# Resume
data = []

# Resume Attributes
data.append(['Confirmados', covid_df_by_date.values[-1][-1]])
data.append(['Recuperados', cases_by_care_by_date[4].values[-1][-1]])
data.append(['Muertes', cases_by_care_by_date[2].values[-1][-1]])
data.append(['Casos descartados', descarted_cases])
data.append(['Importado', covid_df_by_kind[covid_df_by_kind['kind'] == 'Importado'].values[0][-1]])
data.append(['Relacionado', covid_df_by_kind[covid_df_by_kind['kind'] == 'Relacionado'].values[0][-1]])
data.append(['En estudio', covid_df_by_kind[covid_df_by_kind['kind'] == 'En estudio'].values[0][-1]])
data.append(['Muestras procesadas', covid_df_samples_processed.values[-1][-1]])

# Resume Dataframe
covid_df_resume = pd.DataFrame(data=data, columns=['title', 'total'])
# Show dataframe
covid_df_resume.head(10)

# %% [markdown]
# ## Resume
# > ***Output file***: covid_19_resume.csv

# %%
# Save dataframe
covid_df_resume.to_csv(os.path.join(OUTPUT_DIR, 'covid_19_resume.csv'), index=False)

# %% [markdown]
# ---
