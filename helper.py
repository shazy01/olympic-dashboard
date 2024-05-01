import streamlit as st
import pandas as pd
import preprocessor
import numpy as np


def fetch_medal_tally(df, year, country):
    medal_df = df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    flag = 0
    if year == 'Overall' and country == 'Overall':
        temp_df = medal_df
    if year == 'Overall' and country != 'Overall':
        flag = 1
        temp_df = medal_df[medal_df['region'] == country]
    if year != 'Overall' and country == 'Overall':
        temp_df = medal_df[medal_df['Year'] == int(year)]
    if year != 'Overall' and country != 'Overall':
        temp_df = medal_df[(medal_df['Year'] == year) & (medal_df['region'] == country)]

    if flag == 1:
        x = temp_df.groupby('Year').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Year').reset_index()
    else:
        x = temp_df.groupby('region').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Gold',
                                                                                      ascending=False).reset_index()

    x['total'] = x['Gold'] + x['Silver'] + x['Bronze']

    x['Gold'] = x['Gold'].astype('int')
    x['Silver'] = x['Silver'].astype('int')
    x['Bronze'] = x['Bronze'].astype('int')
    x['total'] = x['total'].astype('int')

    return x


def country_year_list(df):
    years = df['Year'].unique().tolist()
    years.sort()
    years.insert(0, 'Overall')

    country = np.unique(df['region'].dropna().values).tolist()
    country.sort()
    country.insert(0, 'Overall')

    return years,country

def data_over_time(df,col):

    nations_over_time = df.drop_duplicates(['Year', col])['Year'].value_counts().reset_index().sort_values('index')
    nations_over_time.rename(columns={'index': 'Edition', 'Year': col}, inplace=True)
    return nations_over_time


def most_successful(df, sport):
    temp_df = df.dropna(subset=['Medal'])

    if sport != 'Overall':
        temp_df = temp_df[temp_df['Sport'] == sport]

    x = temp_df['Name'].value_counts().reset_index().head(15).merge(df, left_on='index', right_on='Name', how='left')[
        ['index', 'Name_x', 'Sport', 'region']].drop_duplicates('index')
    x.rename(columns={'index': 'Name', 'Name_x': 'Medals'}, inplace=True)
    return x

def yearwise_medal_tally(df,country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'], inplace=True)

    new_df = temp_df[temp_df['region'] == country]
    final_df = new_df.groupby('Year').count()['Medal'].reset_index()

    return final_df

def country_event_heatmap(df,country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'], inplace=True)

    new_df = temp_df[temp_df['region'] == country]

    pt = new_df.pivot_table(index='Sport', columns='Year', values='Medal', aggfunc='count').fillna(0)
    return pt


def most_successful_countrywise(df, country):
    temp_df = df.dropna(subset=['Medal'])

    temp_df = temp_df[temp_df['region'] == country]

    x = temp_df['Name'].value_counts().reset_index().head(10).merge(df, left_on='index', right_on='Name', how='left')[
        ['index', 'Name_x', 'Sport']].drop_duplicates('index')
    x.rename(columns={'index': 'Name', 'Name_x': 'Medals'}, inplace=True)
    return x

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

def top_n_countries(df, n):
    top_n = df.groupby('region')['Medal'].count().nlargest(n).reset_index()
    top_n.columns = ['Country', 'Total']
    return top_n


def top_n_sports(df, n):
    top_n = df.groupby('Sport')['Medal'].count().nlargest(n).reset_index()
    top_n.columns = ['Sport', 'Total']
    return top_n


def top_n_sports_country(df, country, n):
    top_n = df[df['region'] == country].groupby('Sport')['Medal'].count().nlargest(n).reset_index()
    top_n.columns = ['Sport', 'Total']
    return top_n


def top_n_athletes(df, n):
    top_n = df.groupby('Name')['Medal'].count().nlargest(n).reset_index()
    top_n.columns = ['Name', 'Total']
    return top_n

def medals_by_sport_gender(df):
    sport_gender_df = df.groupby(['Sport', 'Sex'])['Medal'].count().reset_index()
    sport_gender_df.columns = ['Sport', 'Gender', 'Total']
    return sport_gender_df



def gender_distribution(df):
    gender_sport_df = df.groupby(['Sport', 'Sex'])['ID'].nunique().reset_index()
    gender_sport_df.columns = ['Sport', 'Gender', 'Total']
    return gender_sport_df

def top_n_athletes(df, n):
    top_n = df.groupby('Name')['Medal'].count().nlargest(n).reset_index()
    top_n.columns = ['Name', 'Total']
    return top_n

def medal_distribution(df):
    medal_df = df['Medal'].value_counts().reset_index()
    medal_df.columns = ['Medal', 'Total']
    return medal_df

def top_n_countries_by_medal(df, medal_type, n):
    top_n = df[df['Medal'] == medal_type].groupby('region')['Medal'].count().nlargest(n).reset_index()
    top_n.columns = ['Country', 'Total']
    return top_n


def top_n_sports_by_medal_type(df, n):
    medal_sports = df.groupby(['Sport', 'Medal'])['Medal'].count().reset_index(name='Total')
    top_n_sports = medal_sports.groupby('Sport')['Total'].sum().nlargest(n).reset_index()['Sport'].tolist()
    top_sports_medal_type = medal_sports[medal_sports['Sport'].isin(top_n_sports)]
    return top_sports_medal_type



