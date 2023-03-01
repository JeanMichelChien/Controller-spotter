import folium
import matplotlib.pyplot as plt
import pandas as pd
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from streamlit_option_menu import option_menu

import Controler_spotter_mainfile  # import main file
import streamlit as st

# matplotib: remove background around the figure
plt.rcParams['axes.facecolor'] = 'none'
plt.rcParams['axes.labelcolor'] = 'white'
plt.rcParams['axes.edgecolor'] = 'grey'
plt.rcParams['xtick.color'] = 'white'
plt.rcParams['ytick.color'] = 'white'

# ------------- SETTINGS FOR THE PAGE---------------------------------------------------------
page_title = "CONTROLLER SPOTTER"
page_icon = ":train:"  # emoji
layout = "centered"

# https://youtu.be/3egaMfE9388

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + " " + page_icon)

# Clean streamlit style using CSS
hide_st_style = """ 
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
st.markdown(hide_st_style, unsafe_allow_html=True)  # use this CSS in Streamlit

# ------------------NAVIGATION MENU--------------------------------------------------

menu_selected = option_menu(
    menu_title=None,
    options=["Dashboard", "Statistics"],  # each menus
    icons=["pencil-fill", "bar-chart-fill"],  # https://icons.getbootstrap.com/
    orientation='horizontal'
)
# ------------- IMPORT DATASET FROM OTHER FILE --------------------------

data = Controler_spotter_mainfile.data.copy()  # get dataframe from other file
# data = pd.read_excel(
# r"C:\Users\emeri\OneDrive\Documents\Python Scripts\Projet Controleurs_Spotteurs\V2 - 2023\data.xlsx")

# ----------------------- SLICERS VALUES ----------------------------------------
hours = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19",
         "20", "21", "22", "23"]
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# ----------------------- ON MENU 1: DASHBOARD: -----------------------

if menu_selected == "Dashboard":
    st.header("Data visualization")

    # Create slider Day
    # https://docs.streamlit.io/library/api-reference/widgets/st.select_slider
    day_slider_start, day_slider_end = st.select_slider(
        label=":calendar: Days",
        options=days,  # from list already created
        value=["Monday", "Sunday"],  # default value: start and end (provide only 2 values)
        help="Select the days you want to display in the map"
    )
    # st.write("You selected the period between", day_slider_start, " and ", day_slider_end)
    # convert the day name to day_num so it can be used as numerical value to select between.
    day_dict = {"Monday": "1", "Tuesday": "2", "Wednesday": "3", "Thursday": "4", "Friday": "5", "Saturday": "6",
                "Sunday": "7"}
    daynum_slider_start = int(day_dict[day_slider_start])  # ex: input=Monday, output=1; conversion str to int
    daynum_slider_end = int(day_dict[day_slider_end])

    # Create slider Hour
    hour_slider_start, hour_slider_end = st.select_slider(
        label=":clock1: Hours",
        options=hours,
        value=["0", "23"],  # default
        help="Select the hours you want to display in the map"
    )
    # st.write("You selected the time between", hour_slider_start, ":00 and ", hour_slider_end, ":00")
    st.write("Selection: ", day_slider_start, " to ", day_slider_end, ", from ", hour_slider_start, ":00 to ", hour_slider_end, ":00")

    hour_slider_start = int(hour_slider_start)  # conversion str to int
    hour_slider_end = int(hour_slider_end)

    # Filter the dataframe with the slider values
    conditions = ((data['day_num'] <= daynum_slider_end) &  # create conditions
                  (data['day_num'] >= daynum_slider_start) &
                  (data['time'] <= hour_slider_end) &
                  (data['time'] >= hour_slider_start))
    data_selected = data[conditions]  # apply conditions

    # st.write("Size of the dataframe selected: ", len(data_selected))

    data_selected_heatmap = (data_selected.groupby(by=['Latitude', 'Longitude'])  # prepare data for heatmap
                             .agg({'time': pd.Series.nunique})
                             .sort_values(by='time', ascending=False)
                             .reset_index()
                             .rename(columns={'time': 'occurence'}))
    data_selected_heatmap_list = data_selected_heatmap.values.tolist()  # convert dataframe to list

    # to check: display dataframe to see if filters apply
    # st.dataframe(data_selected)

    # create heatmap
    mapObj = folium.Map(location=[47.3686498, 8.5391825], zoom_start=11)
    folium.TileLayer('openstreetmap').add_to(mapObj)
    # TODO
    mapObj.save(r'C:\Users\emeri\OneDrive\Documents\Python Scripts\Projet Controleurs_Spotteurs\V2 - 2023\output.html')
    HeatMap(data=data_selected_heatmap_list,  # plot data selected on map
            radius=7,
            blur=1).add_to(mapObj)
    # TODO
    mapObj.save(r'C:\Users\emeri\OneDrive\Documents\Python Scripts\Projet Controleurs_Spotteurs\V2 - 2023\output.html')
    st_map = st_folium(
        mapObj,
        width=700,
        height=450
    )

# ----------------------- ON MENU 2: STATISTICS: -----------------------
# No slicers or filtering on this page
if menu_selected == "Statistics":
    st.header(":mag: Explore the data")

    # calculate number of days between min and max date
    timedelta_days = (max(data['date']) - min(data['date'])).days  # return int

    # Chart 1 : top 20 stations ----------------------------------------
    st.header("Top 20 stations by average number of controls per day")
    data_top20_stations = data['station'].value_counts()[:20].sort_values(ascending=False) / timedelta_days
    fig1 = plt.figure()
    fig1.patch.set_facecolor("none")
    plt.bar(data_top20_stations.index, data_top20_stations.values)
    plt.xticks(rotation="vertical")
    st.pyplot(fig1)

    # Chart 2 : number of controls per day ----------------------------------------
    st.header("Average number of controls per day")
    day_count = data['day'].value_counts() / (timedelta_days / 7)
    x_values_day = day_count.index
    y_values_day = day_count.values
    label_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    fig2 = plt.figure()
    fig2.patch.set_facecolor("none")
    plt.bar(x_values_day, y_values_day)
    plt.xticks(x_values_day, label_order, rotation="vertical")
    st.pyplot(fig2)

    # Chart 3 : number of controls per hour ----------------------------------------
    st.header("Average number of controls per hour")
    hour_count = data['time'].value_counts() / timedelta_days
    x_values_hour = hour_count.index
    y_values_hour = hour_count.values
    fig3 = plt.figure()
    fig3.patch.set_facecolor("none")
    plt.bar(x_values_hour, y_values_hour)
    plt.xticks(x_values_hour, rotation="vertical")
    st.pyplot(fig3)

    # Chart 4 : evolution of users reporting controls on the plateform ----------------------------------------
    st.header("Number of users reporting controls over time")
    data_user = data[["date", "from_id"]].copy()  # extract just the 2 needed columns in a new df
    data_user["date"] = data_user["date"].dt.strftime("%Y-%m")  # remove time from datetime
    data_user = data_user.groupby("date")["from_id"].nunique()  # count unique users per day
    fig4 = plt.figure()
    fig4.patch.set_color("none")
    plt.plot(data_user)
    plt.xticks(rotation="vertical")
    st.pyplot(fig4)

    # More statistics (for me)
    total_number_controls = len(data)
    count_stations_controlled = data['station'].nunique()  # distinct count, return int
    st.write("total number of controls : ", total_number_controls)
    st.write("average number of controls per day : ", total_number_controls / timedelta_days)
    st.write("count of unique stations controlled : ", count_stations_controlled)


