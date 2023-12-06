import pandas as pd
import plotly.express as px
import streamlit as st
import numpy as np

st.set_page_config(page_title ="Customer Demography",initial_sidebar_state="expanded", layout="wide", page_icon="💦")

# --- READ DATA ---
cust_merge = pd.read_pickle('data/cust_merge.pkl')
coord = pd.read_csv('data/coordinate.csv')

# --- ROW 1 ---
st.write('# Customer Demography Dashboard')
st.write(""" Explore customer insights effortlessly with our Customer Demographics Dashboard. 
         Gain a quick overview of income distribution, spending scores, and professions. 
         Dive into the details of work experience, family sizes, and more. Uncover patterns and trends to better understand our diverse customer base—all in a single, user-friendly view.""")

# --- ROW 2 ---
col1, col2 = st.columns(2)

col1.write(f'### Distribution of Customers by Income Category') # f-string

category = col1.radio(
    "Select Category",
    ["High", "Medium", "Low"]
)

cust_merge['income_category'] = pd.cut(cust_merge['Annual_Income'], bins=[-float('inf'), 30000000, 60000000, float('inf')], labels=['Low', 'Medium', 'High'])

data_pie = cust_merge[cust_merge['income_category'] == category]

# Buat pie chart interaktif dengan Plotly Express
fig = px.pie(data_pie, names='Profession')
fig.update_layout(showlegend=False)

# Tampilkan pie chart
col1.plotly_chart(fig, use_container_width=True, width=col1.width)

## --- MAP PLOT ---
# data: map
col2.write('### Profession Count across Indonesia')
input_select = col2.selectbox(
    label='Select Profession',
    options=np.sort(cust_merge['Profession'].unique())
)

m = cust_merge[cust_merge['Profession'] == input_select]
prov_prof = pd.crosstab(
    index = m['province'],
    columns = m['gender'],
    colnames = [None]
)
prov_prof['Total'] = prov_prof['Female'] + prov_prof['Male']
df_map = prov_prof.merge(right=coord, on='province')

# plot: map
plot_map = px.scatter_mapbox(data_frame=df_map, lat='latitude', lon='longitude',
                             mapbox_style='carto-positron', zoom=3,
                             size='Total',
                             hover_name='province',
                             custom_data=['Male', 'Female', 'Total']  
                            )
plot_map.update_traces(
    hovertemplate="<b>%{hovertext}</b> <br><br>"
                  "Male : <b>%{customdata[0]}</b> <br>"
                  "Female : <b>%{customdata[1]}</b> <br>"
                  "Total : <b>%{customdata[2]}</b> "
    )   
col2.plotly_chart(plot_map, use_container_width=True)

# --- ROW 3 ---
st.divider()
col3, col4 = st.columns(2)

col3.write(f'### Total Profession Based On Zodiac') # f-string

zodiak = col3.text_input('Insert Zodiak', 'Gemini')

employ_cs = cust_merge[cust_merge['zodiak'].str.lower() == zodiak.lower()]


# --- ROW 4 ---
col5, col6 = st.columns(2)

if employ_cs.empty:
    col5.markdown("<b>Oops.. Data tidak ditemukan</b>", unsafe_allow_html=True)
else:
    df_gen = pd.crosstab(index=employ_cs['Profession'], columns='num_people', colnames=[None])
    df_gen = df_gen.reset_index()

    # plot: barplot
    plot_gen = px.bar(df_gen, x='Profession', y='num_people', 
                       labels = {'Profession' : 'Profession',
                                 'num_people' : 'Total Persons'})

    col5.plotly_chart(plot_gen, use_container_width=True)

## --- INPUT SLIDER ---
col4.write(f'### Work Experience Each Profession') # f-string

input_slider = col4.slider(
    label='Select Work Experience Range (in Year)',
    min_value=cust_merge['Work_Experience'].min(),
    max_value=cust_merge['Work_Experience'].max(),
    value=[0,17]
)

min_slider = input_slider[0]
max_slider = input_slider[1]

## --- BARPLOT ---
# data: barplot
exp = cust_merge[cust_merge['Work_Experience'].between(left=min_slider, right=max_slider)]
avg_income = exp.groupby(['Profession', 'gender'])['Annual_Income'].mean().reset_index().sort_values(by = 'gender')
# plot: barplot
plot_gen = px.bar(avg_income.sort_values(by='Annual_Income'), 
                   x="Annual_Income", y="Profession", 
                   color="gender", 
                   barmode='group',
                   labels = {'Profession' : 'Profession',
                             'gender': 'Gender',
                             'Annual_Income' : 'Average Annual Income'}
                             )


col6.plotly_chart(plot_gen, use_container_width=True)
