from hashlib import new
from itertools import count
import numpy as np

def weight_v_height(df,sport):
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])
    athlete_df['Medal'].fillna('No Medal', inplace=True)
    if sport != 'Overall':
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        return temp_df
    else:
        return athlete_df

def men_vs_women(df):
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    men = athlete_df[athlete_df['Sex'] == 'M'].groupby('Year').count()['Name'].reset_index()
    women = athlete_df[athlete_df['Sex'] == 'F'].groupby('Year').count()['Name'].reset_index()

    final = men.merge(women, on='Year', how='left')
    final.rename(columns={'Name_x': 'Male', 'Name_y': 'Female'}, inplace=True)

    final.fillna(0, inplace=True)

    return final

def country_event_heatmap(df,country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df = temp_df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', "Medal"])
    new_df = temp_df[temp_df.region == country]
    return new_df

def country_wise_medal_tally(df,country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df = temp_df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', "Medal"])
    temp_df = temp_df[temp_df.region == country]
    temp_df = temp_df.groupby('Year').count()['Medal'].reset_index()
    return temp_df


def most_successful_athletes_of_country(df, country):
    temp_df = df.dropna(subset=['Medal'])

    if country != 'Overall':
        temp_df = temp_df[temp_df['region'] == country]

    x = temp_df['Name'].value_counts().reset_index().merge(df, left_on="index", right_on='Name', how='left')[['index', 'Name_x', 'Sport']].rename(columns={'index': 'Name', 'Name_x': 'Medals'}).drop_duplicates()
    return x.head(20)

def most_successful_athletes(df,sport):
    temp_df = df.dropna(subset=['Medal'])
    
    if sport != 'Overall':
        temp_df  = temp_df[temp_df['Sport'] == sport]
    
    x = temp_df['Name'].value_counts().reset_index().merge(df,left_on="index",right_on='Name',how='left')[['index','Name_x','Sport','region']].rename(columns={'index':'Name','Name_x':'Medals'}).drop_duplicates()
    #x = x[x['Sport'] == sport]
    return x.head(20)

def participating_nations_over_time(df,column):
    nations_over_time = df.drop_duplicates(['Year', column])['Year'].value_counts().reset_index().sort_values('index')
    nations_over_time.rename(columns={'index': 'Edition', 'Year': column}, inplace=True)
    return nations_over_time

def overall_analysis(df):
    header = "Top Statistics"
    editions = (df.Year.unique().shape[0]) - 1  # 1906 olympics is not recognized by commitee.
    hosts    = df.City.unique().shape[0]
    sports   = df.Sport.unique().shape[0]
    events   = df.Event.unique().shape[0]
    athletes = df.Name.unique().shape[0]
    nations  = df.region.unique().shape[0]
    analysis = {"Hosts" : hosts,
                "Sports" : sports,
                "Events" : events,
                "Editions": editions,
                "Nations" : nations,
                "Athletes" : athletes
                }
    return analysis,header

def fetch_medal_tally(df,year,country):
    groupByYearflag = 0
    header = ""
    all_medals_tally = df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', "Medal"])
    
    if year == "Overall" and country == "Overall":
        medals_total = all_medals_tally
        header = "Overall Medal Tally"
    elif year == "Overall" and country != "Overall":
        groupByYearflag = 1
        medals_total = all_medals_tally[all_medals_tally.region == country]
        header = "Medal Tally for " + str(country)
    elif year != "Overall" and country == "Overall":
        
        medals_total = all_medals_tally[all_medals_tally.Year == int(year)]
        header = "Medal Tally in year " + str(year)
    elif year != "Overall" and country != "Overall":
        medals_total = all_medals_tally[(all_medals_tally.Year == int(year)) & (all_medals_tally.region == country)]
        header = "Performance of " + str(country) + " in year " + str(year)
        
    if groupByYearflag == 1:
        medals_total = medals_total.groupby('Year').sum()[['Gold', 'Silver', 'Bronze']]
        medals_total['Total'] = medals_total['Gold'] + medals_total['Silver'] + medals_total['Bronze']
        medals_total = medals_total.sort_values("Year", ascending=True).reset_index()

    else:
        medals_total = medals_total.groupby('region').sum()[['Gold', 'Silver', 'Bronze']]
        medals_total['Total'] = medals_total['Gold'] + medals_total['Silver'] + medals_total['Bronze']
        medals_total = medals_total.sort_values(['Total', 'Gold', 'Silver', 'Bronze'], ascending=False).reset_index()

    medals_total['Gold'] = medals_total['Gold'].astype('int')
    medals_total['Silver'] = medals_total['Silver'].astype('int')
    medals_total['Bronze'] = medals_total['Bronze'].astype('int')
    medals_total['Total'] = medals_total['Total'].astype('int')
    
    return medals_total, header

def year_list(df):
    years = df.Year.unique().tolist()
    years.sort()
    years.insert(0, 'Overall')
    return years

def country_list(df):
    countries = np.unique(df.region.dropna().values).tolist()
    countries.sort()
    countries.insert(0, 'Overall')
    return countries


def sports_list(df):
    sports = np.unique(df.Sport.dropna().values).tolist()
    sports.sort()
    sports.insert(0, 'Overall')
    return sports
