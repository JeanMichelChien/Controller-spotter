# IMPORTING
import pandas as pd
import re

# open messages file and stations file
# TODO
raw_data = pd.read_json(
    r'C:\Users\emeri\OneDrive\Documents\Python Scripts\Projet Controleurs_Spotteurs\V2 - 2023\result.json')
stations = pd.read_excel(
    r'C:\Users\emeri\OneDrive\Documents\Python Scripts\Projet Controleurs_Spotteurs\V2 - 2023\Zurich Stations.xlsx')

# NORMALIZE JSON AND CLEANING ============================================================
# json normalize
# the field "text" is sometimes incomplete; extract "text" from "text_entities" instead
data = pd.json_normalize(raw_data['messages'],
                         record_path=['text_entities'],  # flatten at this level
                         meta=['date', 'from_id'],  # add date and user_id
                         errors='ignore')


# create cleaning function
# function to keep only alphabetical characters using regex
# https://qr.ae/preTQa
def only_alphabetical(string):
    result = re.sub(r'[^a-zA-Z ]', "", string)
    return result


def replace_german_letters(string):
    result = string.replace("ä", "a").replace("ö", "o").replace("ü", "u").replace("ë", "e").replace("ï", "i")
    return result


# create function to delete the station name from message after specific words indicating terminus
def delete_after_words(text):
    words_stop = ["richtung", "richtig"]  # list of words indicating end bahnohf
    i = 0
    text_list = text.split()  # transform str sentence to list of words
    while i < len(text_list):
        if text_list[i] in words_stop and i + 1 < len(text_list):
            del text_list[i + 1]
        else:
            i += 1
    return " ".join(str(e) for e in text_list)  # convert list of words to string with space between each words


# cleaning Telegram data
data.drop('user_id', axis=1, inplace=True)  # drop unused field
data['date'] = pd.to_datetime(data['date'])
data['text_before_cleaning'] = data['text']  # backup original text in a new column
data['text'] = data['text'].str.lower()  # lower
data['text'] = data['text'].apply(replace_german_letters)  # replace "ä", "ü", ö using function
data['text'] = data['text'].apply(only_alphabetical)  # replace non ascii using function
data['text'] = data['text'].apply(delete_after_words)  # use function to delete station name after keywords indicating train direction
data['day'] = data['date'].dt.day_name()
data['time'] = data['date'].dt.hour
data['day_num'] = data['day'].map(
    {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6, "Sunday": 7})

# cleaning Station data
stations['Station'] = stations['Station'].apply(replace_german_letters).apply(only_alphabetical)

# SEARCH STATION NAME IN MESSAGE
station_list = list(set(stations['Station'].str.lower().to_list()))  # create list of unique stations


# create function to extract station name from message: if station in message then return station
def extract_station(text):
    for station in station_list:
        if station in text.split():
            return station
    return None


# create "station" column by applying function
data['station'] = data['text'].apply(extract_station)

# stats on station extraction
# % messages with station extracted
percent_station_found = len(data[data['station'].isna()]) / len(data)
print("% messages with station extracted : ", percent_station_found)
# % messages with station not extracted (not found)
print("% messages with station NOT extracted : ", 1 - percent_station_found)

# ADD STATION COORDINATES TO DATAFRAME ============================================================
# keep only rows with station found on dataframe
data_unmapped = data[data['station'].isna()]['text_before_cleaning']
#TODO
data_unmapped.to_excel(r'C:\Users\emeri\OneDrive\Documents\Python Scripts\Projet Controleurs_Spotteurs\V2 - 2023\data_unmapped.xlsx')
data = data[~data['station'].isna()]

# remove duplicate rows (for different train/bus lines) in Station dataframe
stations.drop_duplicates(subset='Station', inplace=True)
# lower station name
stations['Station'] = stations['Station'].str.lower()

data = data.merge(stations,
                  how='left',
                  left_on='station',
                  right_on='Station').drop(['Station', 'ligne'], axis=1)

# export dataframe to excel
# TODO
data.to_excel(
    r'C:\Users\emeri\OneDrive\Documents\Python Scripts\Projet Controleurs_Spotteurs\V2 - 2023\data.xlsx')
print("file saved to excel")
