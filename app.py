
import streamlit as st
import pandas as pd
import preprocessor, helper
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff
import gdown
import requests

def download_file_from_google_drive(google_drive_link, file_name):
    # Extract the file ID from the Google Drive link
    file_id = google_drive_link.split('/')[-2]
    
    # Construct the download URL
    download_url = f"https://drive.google.com/uc?id={file_id}"
    
    try:
        # Send a request to download the file
        response = requests.get(download_url)
        response.raise_for_status()
        
        # Save the file
        with open(file_name, "wb") as f:
            f.write(response.content)
        
        return file_name
    except Exception as e:
        print(f"Error downloading file: {e}")
        return None

# Google Drive sharing links
athlete_events_link = 'https://drive.google.com/file/d/1Y6zhYf-IiZfI3xLiXwu2ZbMGEHFe--Nq/view?usp=sharing'
noc_regions_link = 'https://drive.google.com/file/d/11xYxRNgRI92DPJBT-v-aZUem_PVLTAZT/view?usp=sharing'

# Download the files
athlete_events_output = download_file_from_google_drive(athlete_events_link, 'athlete_events.csv')
noc_regions_output = download_file_from_google_drive(noc_regions_link, 'noc_regions.csv')

if not athlete_events_output or not noc_regions_output:
    print("Failed to download data files. Please check the links or try again later.")
else:
    # Read the downloaded CSV files
    df = pd.read_csv(athlete_events_output)
    region_df = pd.read_csv(noc_regions_output)


# Read the downloaded CSV files
# athlete_events_output=r'C:\Users\HP\Desktop\Olympic_analyis_app-main\Olympic_analyis_app-main\athlete_events.csv'
# noc_regions_output=r'C:\Users\HP\Desktop\Olympic_analyis_app-main\Olympic_analyis_app-main\noc_regions.csv'

# df = pd.read_csv(athlete_events_output)
# region_df = pd.read_csv(noc_regions_output)

# Data preprocessing
df = preprocessor.preprocess(df, region_df)

# Set custom CSS for background image and white background
css = """
body {
    content: "";
    background: url('https://cdn.britannica.com/44/190944-131-7D082864/Silhouette-hand-sport-torch-flag-rings-Olympic-February-3-2015.jpg');
    position: absolute;
    top:0px;
    left:0px;
    height: 100%;
    width:100%;
    z-index: -1;
    opacity: 0.90;
    color: white;
}
.watermark {
    position: fixed;
    bottom: 10px;
    right: 10px;
    opacity: 0.5;
    font-size: 14px;
    z-index: 999;
}
"""
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
st.markdown('<div class="overlay"></div>', unsafe_allow_html=True)
st.markdown('<div class="watermark">Made By - B20CS044 B20CS065</div>', unsafe_allow_html=True)

# Create upper bar
col1, col2 = st.columns([1, 4])
with col1:
    st.image('https://cdn.pixabay.com/photo/2013/07/13/12/33/games-159849_960_720.png')
with col2:
    st.title("Past Olympics Analysis App")

menu_options = ['Medal Tally', 'Overall Analysis', 'Country-wise Analysis', 'Athlete wise Analysis', 'Top-10', 'Additional Plots']
user_menu = st.selectbox("Select an Option", menu_options)

# Implement the rest of your Streamlit app logic here
# ...


# ---------------------------------------------------------------------------------------------------

fig, ax = plt.subplots(figsize=(25, 20),dpi=400)


if user_menu == 'Medal Tally':
    st.sidebar.header("Medal Tally")
    years,country = helper.country_year_list(df)

    selected_year = st.sidebar.selectbox("Select Year",years)
    selected_country = st.sidebar.selectbox("Select Country", country)

    medal_tally = helper.fetch_medal_tally(df,selected_year,selected_country)
    if selected_year == 'Overall' and selected_country == 'Overall':
        st.title("Overall Tally")
    if selected_year != 'Overall' and selected_country == 'Overall':
        st.title("Medal Tally in " + str(selected_year) + " Olympics")
    if selected_year == 'Overall' and selected_country != 'Overall':
        st.title(selected_country + " overall performance")
    if selected_year != 'Overall' and selected_country != 'Overall':
        st.title(selected_country + " performance in " + str(selected_year) + " Olympics")
    st.table(medal_tally)

    st.title("Top 10 Countries by Total Medals")
    top_countries = helper.top_n_countries(df, 10)
    fig = px.bar(top_countries, x='Country', y='Total', text='Total', color='Country')
    st.plotly_chart(fig)

if user_menu == 'Overall Analysis':
    editions = df['Year'].unique().shape[0] - 1
    cities = df['City'].unique().shape[0]
    sports = df['Sport'].unique().shape[0]
    events = df['Event'].unique().shape[0]
    athletes = df['Name'].unique().shape[0]
    nations = df['region'].unique().shape[0]

    st.title("Top Statistics")
    col1,col2,col3 = st.columns(3)
    with col1:
        st.header("Editions")
        st.title(editions)
    with col2:
        st.header("Hosts")
        st.title(cities)
    with col3:
        st.header("Sports")
        st.title(sports)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Events")
        st.title(events)
    with col2:
        st.header("Nations")
        st.title(nations)
    with col3:
        st.header("Athletes")
        st.title(athletes)

    nations_over_time = helper.data_over_time(df,'region')
    fig = px.line(nations_over_time, x="Edition", y="region")
    st.title("Participating Nations over the years")
    st.plotly_chart(fig)

    events_over_time = helper.data_over_time(df, 'Event')
    fig = px.line(events_over_time, x="Edition", y="Event")
    st.title("Events over the years")
    st.plotly_chart(fig)

    athlete_over_time = helper.data_over_time(df, 'Name')
    fig = px.line(athlete_over_time, x="Edition", y="Name")
    st.title("Athletes over the years")
    st.plotly_chart(fig)

    st.title("No. of Events over time(Every Sport)")
    fig,ax = plt.subplots(figsize=(20,20))
    x = df.drop_duplicates(['Year', 'Sport', 'Event'])
    ax = sns.heatmap(x.pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count').fillna(0).astype('int'),
                annot=True)
    st.pyplot(fig)

    st.title("Most successful Athletes")
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0,'Overall')

    selected_sport = st.selectbox('Select a Sport',sport_list)
    x = helper.most_successful(df,selected_sport)
    st.table(x)

    st.title("Top 10 Sports by Total Medals")
    top_sports = helper.top_n_sports(df, 10)
    fig = px.pie(top_sports, values='Total', names='Sport', title='Top 10 Sports by Total Medals')
    st.plotly_chart(fig)

if user_menu == 'Country-wise Analysis':

    st.sidebar.title('Country-wise Analysis')

    country_list = df['region'].dropna().unique().tolist()
    country_list.sort()

    selected_country = st.sidebar.selectbox('Select a Country',country_list)

    country_df = helper.yearwise_medal_tally(df,selected_country)
    fig = px.line(country_df, x="Year", y="Medal")
    st.title(selected_country + " Medal Tally over the years")
    st.plotly_chart(fig)

    st.title(selected_country + " excels in the following sports")
    pt = helper.country_event_heatmap(df,selected_country)
    fig, ax = plt.subplots(figsize=(20, 20))
    ax = sns.heatmap(pt,annot=True)
    st.pyplot(fig)

    st.title("Top 10 athletes of " + selected_country)
    top10_df = helper.most_successful_countrywise(df,selected_country)
    st.table(top10_df)

    st.title(f"Top 5 {selected_country}'s Most Successful Sports")
    top_sports_country = helper.top_n_sports_country(df, selected_country, 5)
    fig = px.bar(top_sports_country, x='Sport', y='Total', text='Total', color='Sport')
    st.plotly_chart(fig)

if user_menu == 'Athlete wise Analysis':
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    x1 = athlete_df['Age'].dropna()
    x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
    x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
    x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()

    fig = ff.create_distplot([x1, x2, x3, x4], ['Overall Age', 'Gold Medalist', 'Silver Medalist', 'Bronze Medalist'],show_hist=False, show_rug=False)
    fig.update_layout(autosize=False,width=1000,height=600)
    st.title("Distribution of Age")
    st.plotly_chart(fig)

    x = []
    name = []
    famous_sports = ['Basketball', 'Judo', 'Football', 'Tug-Of-War', 'Athletics',
                     'Swimming', 'Badminton', 'Sailing', 'Gymnastics',
                     'Art Competitions', 'Handball', 'Weightlifting', 'Wrestling',
                     'Water Polo', 'Hockey', 'Rowing', 'Fencing',
                     'Shooting', 'Boxing', 'Taekwondo', 'Cycling', 'Diving', 'Canoeing',
                     'Tennis', 'Golf', 'Softball', 'Archery',
                     'Volleyball', 'Synchronized Swimming', 'Table Tennis', 'Baseball',
                     'Rhythmic Gymnastics', 'Rugby Sevens',
                     'Beach Volleyball', 'Triathlon', 'Rugby', 'Polo', 'Ice Hockey']
    for sport in famous_sports:
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        x.append(temp_df[temp_df['Medal'] == 'Gold']['Age'].dropna())
        name.append(sport)

    fig = ff.create_distplot(x, name, show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, width=1000, height=600)
    st.title("Distribution of Age wrt Sports(Gold Medalist)")
    st.plotly_chart(fig)

    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')

    st.title('Height Vs Weight')
    selected_sport = st.selectbox('Select a Sport', sport_list)
    temp_df = helper.weight_v_height(df,selected_sport)
    fig,ax = plt.subplots()
    # ax = sns.scatterplot(temp_df['Weight'],temp_df['Height'],hue=temp_df['Medal'],style=temp_df['Sex'],s=60)
    ax = sns.scatterplot(x=temp_df['Weight'], y=temp_df['Height'], hue=temp_df['Medal'], style=temp_df['Sex'], s=60)
    st.pyplot(fig)



    st.title("Men Vs Women Participation Over the Years")
    final = helper.men_vs_women(df)
    fig = px.line(final, x="Year", y=["Male", "Female"])
    fig.update_layout(autosize=False, width=1000, height=600)
    st.plotly_chart(fig)

    st.title("Top 10 Athletes by Total Medals")
    top_athletes = helper.top_n_athletes(df, 10)
    fig = px.bar(top_athletes, x='Name', y='Total', text='Total', color='Name')
    st.plotly_chart(fig)



if user_menu == 'Top-10':
    st.title("Medals by Sport and Gender")
    sport_gender = helper.medals_by_sport_gender(df)
    fig = px.bar(sport_gender, x='Sport', y='Total', text='Total', color='Gender', barmode='group')
    st.plotly_chart(fig)

    st.title("Top 10 Countries by Total Medals")
    top_countries = helper.top_n_countries(df, 10)
    fig = px.bar(top_countries, x='Country', y='Total', text='Total', color='Country')
    st.plotly_chart(fig)

    st.title("Top 10 Sports by Total Medals")
    top_sports = helper.top_n_sports(df, 10)
    fig = px.pie(top_sports, values='Total', names='Sport', title='Top 10 Sports by Total Medals')
    st.plotly_chart(fig)


if user_menu == 'Additional Plots':
    st.title("Gender Distribution in Each Sport")
    gender_sport_df = helper.gender_distribution(df)
    fig = px.bar(gender_sport_df, x='Sport', y='Total', text='Total', color='Gender', barmode='group')
    st.plotly_chart(fig)

    st.title("Top 10 Athletes by Total Medals")
    top_athletes = helper.top_n_athletes(df, 10)
    fig = px.bar(top_athletes, x='Name', y='Total', text='Total', color='Name')
    st.plotly_chart(fig)

    st.title("Medals Distribution by Medal Type")
    medal_distribution = helper.medal_distribution(df)
    fig = px.pie(medal_distribution, values='Total', names='Medal', title='Medals Distribution by Medal Type')
    st.plotly_chart(fig)

    st.title("Top 10 Countries by Gold Medals")
    top_countries_gold = helper.top_n_countries_by_medal(df, 'Gold', 10)
    fig = px.bar(top_countries_gold, x='Country', y='Total', text='Total', color='Country')
    st.plotly_chart(fig)

    st.title("Top 10 Sports by Medal Type")
    top_sports_medal_type = helper.top_n_sports_by_medal_type(df, 10)
    fig = px.bar(top_sports_medal_type, x='Sport', y='Total', text='Total', color='Medal', barmode='group')
    st.plotly_chart(fig)






