from googleapiclient.discovery import build
import pymongo
from pymongo import MongoClient
import psycopg2
import pandas as pd
import streamlit as st

#connecting to youtube using API Key
youtube = build("youtube","v3", developerKey="AIzaSyBL7yL9AMdjU7yvwz_VcdM61vNqiA8NYiQ")

#connecting to SQL
mydb=psycopg2.connect(
    host="localhost",
    user="postgres",
    password="risehigh07",
    database="youtube_data"
    )
mycursor=mydb.cursor()

#connecting to MongoDB compass
client=pymongo.MongoClient("mongodb://localhost:27017")
db=client["YouTube_Data"]

#creating a function to get channel information when a channel Id is provided
def channel_information(Channel_id):
        request = youtube.channels().list(
                part="snippet,statistics,status,topicDetails,contentDetails",
                id=Channel_id
        )
        response = request.execute()
        
        for i in response['items']:
                data = dict(Channel_Name=i["snippet"]["title"],
                        Channel_id=i["id"],
                        Subscription_counts=i["statistics"]["subscriberCount"],
                        Channel_Views=i["statistics"]['viewCount'],
                        Total_Videos=i["statistics"]['videoCount'],
                        Channel_Description=i["snippet"]['description'],
                        Channel_status=i['status']['privacyStatus'],
                        Channel_type=i['topicDetails']['topicCategories'],
                        Playlist_id=i['contentDetails']['relatedPlaylists']['uploads'])
        return data

#to get the details of playlist
def get_playlist_details(Channel_ID):
        next_page_token=None
        All_Data=[]
        while True:
                request=youtube.playlists().list(
                part="snippet,contentDetails",
                channelId=Channel_ID,
                maxResults=50,
                pageToken=next_page_token
                )
                response=request.execute()
                for item in response['items']:
                        data=dict(Playlist_ID=item['id'],
                        Playlist_name=item['snippet']['title'],
                        Channel_ID=item['snippet']['channelId'],
                        Channel_Name=item['snippet']['channelTitle'],
                        PublishedAt=item['snippet']['publishedAt'],
                        Video_Count=item['contentDetails']['itemCount']
                        )
                All_Data.append(data)
                next_page_token=response.get('nextPageToken')
                if next_page_token is None:
                        break
        return All_Data

#creating a function to get information about all the video id of the channel when channel id is provided
def all_video_info(Channel_id):
        Video_id=[]
        response=youtube.channels().list(id=Channel_id,
                                        part='contentDetails').execute()
        playlist_id=response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        next_page_tokens=None
        while True:
                request = youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_id ,
                maxResults=50,
                pageToken=next_page_tokens).execute()
                for i in range(len(request["items"])):
                        Video_id.append(request["items"][i]['snippet']['resourceId']['videoId'])
                
                next_page_tokens=request.get('nextPageToken')
                
                if next_page_tokens is None:
                        break
        return Video_id

#creating a function to get comment information when video id is provided
def comment_information(Video_id):
        Comment_data=[]
        try:
                for video_ids in Video_id:
                        request=youtube.commentThreads().list(
                                        part="snippet",
                                        videoId=video_ids,
                                        maxResults=50
                        )
                        response=request.execute()
                        
                        for item in response['items']:
                                data=dict(Comment_ID=item['snippet']['topLevelComment']['id'],
                                        Video_id=item['snippet']['topLevelComment']['snippet']['videoId'],
                                        Comment_text=item['snippet']['topLevelComment']['snippet']['textDisplay'],
                                        Comment_Author=item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                                        Comment_Published=item['snippet']['topLevelComment']['snippet']['publishedAt']
                                        )
                                Comment_data.append(data)
        except:
                pass
        return Comment_data

#creating a function to get information about each video when video id is provided
#creating a function to get information about each video when video id is provided
def get_video_information(Video_id):
        video_data=[]
        for video_ids in Video_id:
                request=youtube.videos().list(
                        part="snippet,contentDetails,statistics",
                        id=video_ids
                )
                response=request.execute()
                for i in response['items']:
                        data=dict(Video_id=i['id'],
                                Channel_name=i["snippet"]['channelTitle'],
                                Channel_id=i["snippet"]['channelId'],
                                Video_name=i['snippet']["title"],
                                Description=i['snippet']['description'],
                                Published_Date=i['snippet']['publishedAt'],
                                Views=i['statistics']['viewCount'],
                                Likes=i['statistics'].get("likeCount"),
                                Favorite_count=i['statistics'].get('favoriteCount'),
                                Comments=i['statistics']['commentCount'],
                                Tags=i['snippet'].get('tags',),
                                Duration=i['contentDetails']['duration'],
                                Thumbnail=i['snippet']['thumbnails'],
                                Caption_status=i['contentDetails']['caption'],                                
                                Definition=i['contentDetails']['definition']
                                )
                        video_data.append(data)
        return video_data

# Function Block that consists of five other functions to get the details from channel ID
def channel_details(Channel_ID):
        Channel_Detail=channel_information(Channel_ID)
        Playlist_Detail=get_playlist_details(Channel_ID)
        Video_Ids=all_video_info(Channel_ID)
        Video_info=get_video_information(Video_Ids)
        Comment_details=comment_information(Video_Ids)

        col1=db["Channel Details"]
        col1.insert_one({"channel_information":Channel_Detail,"playlist_information":Playlist_Detail,
                                "video_information":Video_info,"comment_information":Comment_details})
        return "Upload Completed Successfully"

#creating a table for channels in sql database
def channels_table():
        mydb=psycopg2.connect(
                host="localhost",
                user="postgres",
                password="risehigh07",
                database="youtube_data"
                )
        mycursor=mydb.cursor()
        drop='''drop table if exists channels'''
        mycursor.execute(drop)
        mydb.commit()

        try:
                query='''create table if not exists channels(Channel_Name varchar(255),
                                                Channel_id varchar(255) primary key,
                                                Subscription_counts bigint,
                                                Channel_Views bigint,
                                                Total_Videos bigint,
                                                Channel_Description text,
                                                Channel_status varchar(50),
                                                Playlist_id varchar(255));'''
                mycursor.execute(query)
                mydb.commit()
        except:
                st.write("Channel table is created already")

        ch_list=[]
        db=client["YouTube_Data"]
        coll1=db["Channel Details"]
        for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
                ch_list.append(ch_data["channel_information"])
        df=pd.DataFrame(ch_list)

        for index,row in df.iterrows():
                insert='''insert into channels(Channel_Name ,
                                                Channel_id ,
                                                Subscription_counts,
                                                Channel_Views,
                                                Total_Videos,
                                                Channel_Description,
                                                Channel_status ,
                                                Playlist_id)
                                                
                                                values(%s,%s,%s,%s,%s,%s,%s,%s)'''
                values=(row['Channel_Name'],
                        row["Channel_id"],
                        row["Subscription_counts"],
                        row["Channel_Views"],
                        row["Total_Videos"],
                        row["Channel_Description"],
                        row["Channel_status"],
                        row["Playlist_id"])
                try:
                        mycursor.execute(insert,values)
                        mydb.commit()
                except:
                        st.write("Channel values are inserted already")
                
                
#creating a table for comments
def comments_table():
        mydb=psycopg2.connect(
                host="localhost",
                user="postgres",
                password="risehigh07",
                database="youtube_data"
                )

        mycursor=mydb.cursor()
        drop='''drop table if exists comments'''
        mycursor.execute(drop)
        mydb.commit()

        try:
                create_query = '''CREATE TABLE if not exists comments(Comment_ID varchar(255) primary key,
                Video_id varchar(255),
                Comment_text text, 
                Comment_Author varchar(255),
                Comment_Published timestamp)'''
                
                mycursor.execute(create_query)
                mydb.commit()

        except:
                st.write("Comment table is created already")
                
        com_list = []
        db = client["YouTube_Data"]
        coll1 = db["Channel Details"]
        for com_data in coll1.find({},{"_id":0,"comment_information":1}):
                for i in range(len(com_data["comment_information"])):
                        com_list.append(com_data["comment_information"][i])
        df = pd.DataFrame(com_list)
        df["Comment_Published"]=df["Comment_Published"].str.replace("Z","")
        df["Comment_Published"]=df["Comment_Published"].str.replace("T"," ")

        for index, row in df.iterrows():
                insert_query = '''INSERT INTO comments (Comment_ID,
                                                Video_id,
                                                Comment_text, 
                                                Comment_Author,
                                                Comment_Published)
                                                
                                                values (%s, %s, %s, %s, %s)'''

                values = (row['Comment_ID'],
                        row['Video_id'],
                        row['Comment_text'],
                        row['Comment_Author'],
                        row['Comment_Published']
                        )
                try:
                        mycursor.execute(insert_query,values)
                        mydb.commit()
                except:
                        st.write("Comment values are inserted already")


#function to create table for videos
def videos_table():
        mydb=psycopg2.connect(
                host="localhost",
                user="postgres",
                password="risehigh07",
                database="youtube_data"
                )
        mycursor=mydb.cursor()
                
        drop='''drop table if exists videos'''
        mycursor.execute(drop)
        mydb.commit()
        
        try:
                create_query = '''create table if not exists videos(Video_id varchar(255) primary key,
                                                Channel_name varchar(255),
                                                Channel_id varchar(255),
                                                Title varchar(255),
                                                Description text,
                                                Published_Date timestamp,
                                                Views bigint,
                                                Likes bigint,
                                                Favorite_count bigint,
                                                Comments bigint,
                                                Tags text,
                                                Duration interval,
                                                Thumbnail varchar(225),
                                                Caption_status varchar(255),
                                                Definition varchar(255))'''
                mycursor.execute(create_query)             
                mydb.commit()
        
        except:
                st.write("Videos Table is created already")
                
        vi_list = []
        db = client["YouTube_Data"]
        col1 = db["Channel Details"]
        for vi_data in col1.find({},{"_id":0,"video_information":1}):
                for i in range(len(vi_data["video_information"])):
                        vi_list.append(vi_data["video_information"][i])
        df = pd.DataFrame(vi_list)
        df["Published_Date"]=df["Published_Date"].str.replace("Z","")
        df["Published_Date"]=df["Published_Date"].str.replace("T"," ")
        df["Published_Date"]=df["Published_Date"].str.replace("T"," ")
        df['Thumbnail']=df['Thumbnail'][0]['default']['url']
        df['Caption_status']=df['Caption_status'].str.replace("false","no caption")
        
        for index, row in df.iterrows():
            insert_query = '''
                        INSERT INTO videos (
                                        Video_id,
                                        Channel_name,
                                        Channel_id,
                                        Title,
                                        Description,
                                        Published_Date,
                                        Views,
                                        Likes,
                                        Favorite_count,
                                        Comments,
                                        Tags,
                                        Duration,
                                        Thumbnail,
                                        Caption_status,
                                        Definition
                                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''

            values = ( row['Video_id'],
                    row['Channel_name'],
                    row['Channel_id'],
                    row['Video_name'],
                    row['Description'],
                    row['Published_Date'],
                    row['Views'],
                    row['Likes'],
                    row['Favorite_count'],
                    row['Comments'],                
                    row['Tags'],                
                    row['Duration'],                
                    row['Thumbnail'],
                    row['Caption_status'],
                    row['Definition'])
            try:
                    mycursor.execute(insert_query,values)
                    mydb.commit()
            except:
                st.write("videos values already are inserted")
                
                
#creating a table for playlist 
def playlists_table():
        mydb=psycopg2.connect(
                host="localhost",
                user="postgres",
                password="risehigh07",
                database="youtube_data"
                )
        mycursor=mydb.cursor()    
        drop='''drop table if exists playlists'''
        mycursor.execute(drop)
        mydb.commit()
        try:
                query='''create table if not exists playlists(Playlist_ID varchar(255) primary key,
                                                                Playlist_name varchar(255),
                                                                Channel_ID varchar(255),
                                                                Channel_Name varchar(255),
                                                                Video_Count bigint)'''
                mycursor.execute(query)
                mydb.commit()
        except:
                st.write("Playlists Table is created already")

        db = client["YouTube_Data"]
        col1 =db["Channel Details"]
        pl_list = []
        for pl_data in col1.find({},{"_id":0,"playlist_information":1}):
                for i in range(len(pl_data["playlist_information"])):
                        pl_list.append(pl_data["playlist_information"][i])
        df = pd.DataFrame(pl_list) 
        for index,row in df.iterrows():
                insert='''insert into playlists(Playlist_ID,
                                                        Playlist_name,
                                                        Channel_ID,
                                                        Channel_Name,
                                                        Video_Count)

                                                values(%s,%s,%s,%s,%s)'''
                values=(row['Playlist_ID'],
                        row["Playlist_name"],
                        row["Channel_ID"],
                        row["Channel_Name"],
                        row["Video_Count"]
                )
                
                try:
                        mycursor.execute(insert,values)
                        mydb.commit()
                except:
                        st.write("Playlists Table is created already")


# Function Block that consists of four other functions to create tables such as channels,playlists,videos and comments
def tables():
        channels_table()
        playlists_table()
        videos_table()
        comments_table()
        return "Tables Created Successfully"


#functions to show the tables containing channel details
def display_channels_table():
    ch_list=[]
    db=client["YouTube_Data"]
    coll1=db["Channel Details"]
    for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
        ch_list.append(ch_data["channel_information"])
    channels_table=st.dataframe(ch_list)
    return channels_table

#functions to show the tables containing playlist details
def display_playlists_table():
    db = client["YouTube_Data"]
    coll1 =db["Channel Details"]
    pl_list = []
    for pl_data in coll1.find({},{"_id":0,"playlist_information":1}):
        for i in range(len(pl_data["playlist_information"])):
                pl_list.append(pl_data["playlist_information"][i])
    playlists_table = st.dataframe(pl_list)
    return playlists_table

#functions to show the tables containing video details
def display_videos_table():
    vi_list = []
    db = client["YouTube_Data"]
    coll2 = db["Channel Details"]
    for vi_data in coll2.find({},{"_id":0,"video_information":1}):
        for i in range(len(vi_data["video_information"])):
            vi_list.append(vi_data["video_information"][i])
    videos_table = st.dataframe(vi_list)
    return videos_table

#functions to show the tables containing comments details
def display_comments_table():
    com_list = []
    db = client["YouTube_Data"]
    coll3 = db["Channel Details"]
    for com_data in coll3.find({},{"_id":0,"comment_information":1}):
        for i in range(len(com_data["comment_information"])):
            com_list.append(com_data["comment_information"][i])
    comments_table = st.dataframe(com_list)
    return comments_table

page_bg_img='''
<style>
[data-testid="stAppViewContainer"]{
    background-color:#101010;   
}
</style>'''
st.markdown(page_bg_img,unsafe_allow_html=True)
st.title(":red[YOUTUBE DATA HARVESTING AND WAREHOUSING]")

st.divider()   
channel_id = st.text_input(":red[Channel ID]")
channels = channel_id.split(',')
channels = [ch.strip() for ch in channels if ch]
from PIL import Image
img=Image.open("yt.png")
with st.sidebar:
    st.image(img)
    st.header(":white[_Welcome to YouTube Channel Analytics platform, designed to provide you with insights about any YouTube channel. With the ability to input a YouTube channel ID, this tool empowers you to retrieve data including channel name, subscriber count, total video count, playlist ID, video ID, and metrics such as likes, dislikes, and comments for each video.:rocket:_]")
    
col1, col2 = st.columns(2)
with col1:
    button1 = st.button("Collect Data",type="primary")

with col2:
    button2 = st.button("Migrate Data to SQL",type="primary")

if button1:
    for channel in channels:
        ch_ids = []
        db = client["YouTube_Data"]
        col1 = db["Channel Details"]
        for ch_data in col1.find({},{"_id":0,"channel_information":1}):
            ch_ids.append(ch_data["channel_information"]["Channel_id"])
        if channel in ch_ids:
            st.success("Channel details of the given channel id: " + channel + " already exists")
        else:
            output = channel_details(channel)
            st.success(output)
            
if button2:
    display = tables()
    st.success(display)
    
display_table = st.radio(":red[_SELECT THE TABLE BELOW TO VIEW_]",(":red[Channels]",":red[Playlists]",":red[Videos]",":red[Comments]"))

if display_table == ":red[Channels]":
    display_channels_table()
elif display_table == ":red[Playlists]":
    display_playlists_table()
elif display_table ==":red[Videos]":
    display_videos_table()
elif display_table == ":red[Comments]":
    display_comments_table()

question = st.selectbox(':red[Curated Inquiries]',
                        ('Please Select Your Question',
                        '1. Video and Channel Names Overview',
                        '2. Top Video Producers',
                        '3. Top 10 Most Viewed Videos',
                        '4. Comments Breakdown',
                        '5. Likes Leaderboard',
                        '6. Likes Analysis',
                        '7. Channel View Totals',
                        '8. 2022 Channel Publishers',
                        '9. Average Video Duration by Channel',
                        '10. Comment Champions'))


if question == '1. Video and Channel Names Overview':
    query1 = "select Title as videos, Channel_name as ChannelName from videos;"
    mycursor.execute(query1)
    mydb.commit()
    t1=mycursor.fetchall()
    st.write(pd.DataFrame(t1, columns=["Video Title","Channel Name"]))
    
elif question == '2. Top Video Producers':
    query2 = "select Channel_name as ChannelName,Total_Videos as No_of_Videos from channels order by Total_videos desc;"
    mycursor.execute(query2)
    mydb.commit()
    t2=mycursor.fetchall()
    st.write(pd.DataFrame(t2, columns=["Channel Name","No Of Videos"]))

elif question == '3. Top 10 Most Viewed Videos':
    query3 = '''select Views as views , Channel_name as ChannelName,Title as VideoTitle from videos 
                        where Views is not null order by Views desc limit 10;'''
    mycursor.execute(query3)
    mydb.commit()
    t3 = mycursor.fetchall()
    st.write(pd.DataFrame(t3, columns = ["Views","Channel Name","Video title"]))
    
elif question == '4. Comments Breakdown':
    query4 = "select Comments as No_comments ,Title as VideoTitle from videos where Comments is not null;"
    mycursor.execute(query4)
    mydb.commit()
    t4=mycursor.fetchall()
    st.write(pd.DataFrame(t4, columns=["No Of Comments", "Video Title"]))

elif question == '5. Likes Leaderboard':
    query5 = '''select Title as VideoTitle, Channel_name as ChannelName, Likes as LikesCount from videos 
    where Likes is not null order by Likes desc;'''
    mycursor.execute(query5)
    mydb.commit()
    t5 = mycursor.fetchall()
    st.write(pd.DataFrame(t5, columns=["Video Title","Channel Name","Like count"]))
    
elif question == '6. Likes Analysis':
    query6 = '''select Likes as likeCount,Title as VideoTitle from videos order by likecount desc;'''
    mycursor.execute(query6)
    mydb.commit()
    t6 = mycursor.fetchall()
    st.write(pd.DataFrame(t6, columns=["Like count","Video title"]))
    
elif question == '7. Channel View Totals':
    query7 = "select Channel_Name as ChannelName, Channel_Views as Channelviews from channels;"
    mycursor.execute(query7)
    mydb.commit()
    t7=mycursor.fetchall()
    st.write(pd.DataFrame(t7, columns=["Channel Name","Total Views"]))
    
elif question == '8. 2022 Channel Publishers':
    query8 = '''select Title as Video_Title, Published_Date as VideoRelease, Channel_name as ChannelName from videos 
                where extract(year from Published_Date) = 2022;'''
    mycursor.execute(query8)
    mydb.commit()
    t8=mycursor.fetchall()
    st.write(pd.DataFrame(t8,columns=["Name", "Video Publised On", "Channel Name"]))
    
elif question == '9. Average Video Duration by Channel':
    query9 =  "SELECT Channel_name as ChannelName,AVG(Duration) as averageduration FROM videos group by Channel_name;"
    mycursor.execute(query9)
    mydb.commit()
    t9=mycursor.fetchall()
    df9=pd.DataFrame(t9, columns=['ChannelName', 'averageduration'])
    T9=[]
    for index, row in df9.iterrows():
        channel_title = row['ChannelName']
        average_duration = row['averageduration']
        average_duration_str = str(average_duration)
        T9.append(dict(ChannelTitle=channel_title ,AverageDuration=average_duration_str))
    df=pd.DataFrame(T9)
    df['AverageDuration']=df['AverageDuration'].str.replace("0 days ","")
    st.write(df)

elif question == '10. Comment Champions':
    query10 = '''select Title as VideoTitle, Channel_name as ChannelName, Comments as Comments from videos 
    where Comments is not null order by Comments desc;'''
    mycursor.execute(query10)
    mydb.commit()
    t10=mycursor.fetchall()
    st.write(pd.DataFrame(t10, columns=['Video Title', 'Channel Name', 'NO Of Comments']))
