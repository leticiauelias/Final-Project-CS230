"""
Class: CS230--Section 004
Name: Leticia Usberti Elias
Description: CS230 Final Project
I pledge that I have completed the programming assignment independently.
I have not copied the code from a student or any source.
I have not given my code to any student.
"""

import webbrowser as web
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk


def read_data():
    data = pd.read_csv("Boston Crime Data.csv",
                       header=0,
                       names=["Incident_Number", "Code", "Code_Group", "Description",
                              "District", "Reporting_Area", "Shooting", "Date",
                              "Year", "Month", "Day_of_Week", "Hour",
                              "UCR_Part", "Street", "latitude", "longitude", "Location"]).set_index('Incident_Number')

    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    data.Day_of_Week = pd.Categorical(data.Day_of_Week, categories=weekdays, ordered=True)

    return data


def offenses():
    data2 = read_data()
    offenses_list = []
    for ind, row in data2.iterrows():
        if row['Description'] not in offenses_list:
            offenses_list.append(row['Description'])
    offenses_list.sort()
    return offenses_list


def count_offenses(offense_list, df):
    return [df.loc[df['Description'].isin([offense])].shape[0] for offense in offense_list]


def generate_bar_chart(x, y, selection):
    color = st.sidebar.color_picker('Pick a color for the Bar Chart')
    plt.figure()
    plt.title(f"Top {selection} Offenses & Frequencies")
    plt.barh(x, y, color=color)
    plt.xlabel('Frequencies')
    plt.ylabel('Types of Offense')
    plt.grid(color='black', linestyle='--', linewidth=0.5)

    return plt


def time_period(column='Month'):
    data2 = read_data()
    time_list = []
    for ind, row in data2.iterrows():
        if row[column] not in time_list:
            time_list.append(row[column])
    time_list.sort()
    return time_list


def count_column(list, df, column):
    return [df.loc[df[column].isin([l])].shape[0] for l in list]


def generate_bar_chart2(x, y, column):
    color = st.sidebar.color_picker('Pick a color for the Bar Chart')
    plt.figure()

    plt.bar(x, y, color=color, width=0.5)
    plt.title(f"Total Crime per {column}")
    plt.xlabel(f'{column}')
    plt.xticks(rotation=45)
    plt.ylabel(f'Total Crime')
    plt.grid(color='black', linestyle='--', linewidth=0.5)

    return plt


def generate_pie_chart(frequency, selected_offenses):
    plt.figure()

    explodes = [0 for i in range(len(frequency))]
    maximum = frequency.index(np.max(frequency))
    explodes[maximum] = 0.05
    plt.pie(frequency, labels=selected_offenses, explode=explodes, autopct="%.1f%%")
    plt.title(f"Pie Chart of Offenses in Boston ")
    return plt


def generate_map(dataframe):
    map_df = dataframe.filter(['Description', 'latitude', 'longitude'])

    view_state = pdk.ViewState(latitude=map_df['latitude'].mean(),
                               longitude=map_df['longitude'].mean(),
                               zoom=7,
                               pitch=0.5)

    layer1 = pdk.Layer('ScatterplotLayer',
                       data=map_df,
                       get_position='[longitude, latitude]',
                       get_radius=30,
                       get_color=[255, 0, 255],
                       pickable=True)

    tool_tip = {'html': 'Offenses:<br><b>{Description}</b>', 'style': {'backgroundColor': 'steelblue', 'color': 'white'}}

    map1 = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',
                    initial_view_state=view_state,
                    layers=[layer1],
                    tooltip=tool_tip)

    st.pydeck_chart(map1)


def freq_dict_create(x, y):
    frequency_dict = {}
    for key in x:
        for value in y:
            frequency_dict[key] = value
            y.remove(value)
            break

    frequency_dict_sorted = dict(sorted(frequency_dict.items(), key=lambda item: item[1], reverse=True))
    frequency = list(frequency_dict_sorted.values())
    f_list = list(frequency_dict_sorted.keys())

    return frequency, f_list


st.title('Exploring Crime in Boston')

st.sidebar.title("Select one of the options: ")

options = ["Homepage", "See Original DataFrame", "Filtering the Dataset",
           "Top Offenses - Bar Chart", "Offenses Pie Chart", "Offenses by [Time Period]",
           "Boston Map & Offense Location", "Safety & Reporting Links"]

selected_option = st.sidebar.selectbox("Explore the 'Boston Crime Data' Dataset: ", options)

data = read_data()

# HomePage
if selected_option == options[0]:
    st.success("Open the SIDEBAR tab to explore the Boston Crime Dataset below")
    st.image('crime_in_boston_image.jpg', caption='Image Source: https://www.bostonherald.com/2021/08/07/editorial-tackling-crime-must-address-victims-needs/')
    st.subheader("About the Dataset: ")
    st.write("The 'Boston Crime Data' dataset contains records of offenses committed in Boston on the first quarter of 2022. It includes information about the types of offenses, the specific date/time in which it was reported, and the location (with latitude and longitude) in which it took place. Users will be able to explore the statistics using the sidebar options.  ")
    st.write("If you have any question about the interface please feel free to reach out to me by email: lusbertielias@falcon.bentley.edu")

# See Original DataFrame
elif selected_option == options[1]:
    st.write("This is the Original DataFrame")
    st.write(data)
    rows = len(data.index)
    st.write(f"Total Quantity of Offenses: {rows}")

# I cleaned the DataFrame and allow user to filter based on certain Columns
elif selected_option == options[2]:
    st.write("This is the DataFrame after cleaning the data and allowing for you to filter based on different columns")
    data.pop("Code_Group")
    data.pop("UCR_Part")

    options = st.multiselect('Choose specific Columns to filter the DataFrame:',
                             ["Code", "Description",
                              "District", "Reporting_Area", "Street",
                              "Date", "Year", "Month", "Day_of_Week", "Hour"])
    df2 = data.filter(options)

    st.write(df2)

# Bar Chart of Offense Frequency
elif selected_option == options[3]:
    st.write("Here you can explore the different types of offenses that were committed in Boston:")
    top_options = [5, 10, 15, 20]
    selection = st.sidebar.selectbox("Select a Top Value: ", top_options)

    x = offenses()
    y = count_offenses(offenses(), data)
    bar1_freq, offenses = freq_dict_create(x, y)

    x = offenses[:selection]
    y = bar1_freq[:selection]

    st.pyplot(generate_bar_chart(x, y, selection))

    df2 = pd.DataFrame(offenses[:selection], columns=['Offense Description'])
    df2['Frequency'] = bar1_freq[:selection]
    df2.index += 1
    st.write(df2)

# Pie Chart of Offenses in Boston
elif selected_option == options[4]:
    offenses = offenses()
    options = st.multiselect("Select the types of offenses to add to your Pie Chart: ", offenses, default=['VERBAL DISPUTE', 'INVESTIGATE PROPERTY'])
    offense_list = options
    counts = count_offenses(offense_list, data)
    st.pyplot(generate_pie_chart(counts, offense_list))

# Offenses by [Time Period] with st.radio
elif selected_option == options[5]:

    options = ['Month', 'Day_of_Week', 'Hour']
    select = st.radio("Pick a Time Period to use in the Bar Chart: ", options)

    x = time_period(select)
    y = count_column(x, data, select)

    bar2_freq, offenses = freq_dict_create(x, y)

    st.pyplot(generate_bar_chart2(offenses, bar2_freq, select))

    df3 = pd.DataFrame(offenses, columns=[f'{select}'])
    df3['Quantity of Offenses'] = bar2_freq
    df3.index += 1
    st.write(df3)

# Map of Boston with all of offenses
elif selected_option == options[6]:
    generate_map(data)

# Links to help people who want to report a crime
elif selected_option == options[7]:
    st.write("Here are a few links if you need help reporting a crime in Boston:")

    if st.button("Safety Tips"):
        web.open_new_tab('https://bpdnews.com/tips/')

    elif st.button("Emergency 911"):
        web.open_new_tab('https://bpdnews.com/emergency-911/')

    elif st.button("Boston's Most Wanted List"):
        web.open_new_tab('https://bpdnews.com/most-wanted/')

    elif st.button("Boston's Police Departments "):
        web.open_new_tab('https://bpdnews.com/districts')

    elif st.button("Bentley Campus Security Report"):
        web.open_new_tab('https://www.bentley.edu/files/pdf/Final_ASR.pdf')
        

