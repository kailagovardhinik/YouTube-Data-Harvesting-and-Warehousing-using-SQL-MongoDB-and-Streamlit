from googleapiclient.discovery import build
import pymongo
from pymongo import MongoClient
import mysql.connector
import pandas as pd
import streamlit as st


#connecting to youtube using API Key
youtube = build("youtube","v3", developerKey="AIzaSyDj5WwmFp4Qu03Px3qKzU0o0KsdrV_IJsw")


#connecting to SQL
mydb=mysql.connector.connect(
    host="localhost",
    user="root",
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
                                Description=i.get('description'),
                                Published_Date=i['snippet']['publishedAt'],
                                Views=i.get('viewCount'),
                                Likes=i.get('likeCount'),
                                Favorite_count=i['statistics']['favoriteCount'],
                                Comments=i.get('commentCount'),
                                Tags=i.get('tags'),
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
                        "video_information":Video_Ids,"comment_information":Comment_details})
    return ""Data has been uploaded successfully""

#creating a table for channels in mysql database
def channels_table():
    drop='''drop table if exists channels'''
    mycursor.execute(drop)
    mydb.commit()

    try:
        query='''create table if not exists channels(Channel_id varchar(255),
                                                    Channel_name varchar(255),
                                                    Channel_type varchar(255),
                                                    Channel_views int,
                                                    Channel_description text,
                                                    Channel_status varchar(255),
                                                    Subscribers int,
                                                    Total_videos int,
                                                    Playlist_ID varchar(255)
                                                    )'''
        mycursor.execute(query)
        mydb.commit()
        
    except:
        st.write("Channel table is created already")
        
    ch_list=[]
    db=client["Youtube_data"]
    coll1=db["Channel Details"]
    for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
        ch_list.append(ch_data["channel_information"])
    df=pd.DataFrame(ch_list)

    for index,row in df.iterrows():
        insert='''insert into channels(Channel_id,
                                Channel_name,
                                Channel_type,
                                Channel_views,
                                Channel_description,
                                Channel_status,
                                Subscribers,
                                Total_videos,
                                Playlist_ID)
                                    
                                values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'''  

        values=(row['Channel_id'],
                row["Channel_Name"],
                row["Channel_type"],
                row["Channel_Views"],
                row["Channel_Description"],
                row["Channel_status"],
                row["Subscription_counts"],
                row["Total_Videos"],
                row["Playlist_id"])
        try:
            mycursor.execute(insert,values)
            mydb.commit()
        except:
            st.write("Channel values are inserted already")


#creating a table for playlist 
def playlists_table():
    drop='''drop table if exists playlists'''
    mycursor.execute(drop)
    mydb.commit()

    try:
        create_query = '''create table if not exists playlists(Playlist_Id varchar(255) primary key,
                        Playlist_Name varchar(255), 
                        Channel_Id varchar(255), 
                        Channel_Name varchar(255),
                        PublishedAt timestamp,
                        VideoCount int
                        )
                        '''
        mycursor.execute(create_query)
        mydb.commit()
    except:
        st.write("Playlists Table is created already")
        b = client["Youtube_data"]
    
    col1 =db["Channel Details"]
    pl_list = []
    for pl_data in col1.find({},{"_id":0,"playlist_information":1}):
        for i in range(len(pl_data["playlist_information"])):
                pl_list.append(pl_data["playlist_information"][i])
    df = pd.DataFrame(pl_list)
    
    for index,row in df.iterrows():
        insert_query = '''INSERT into playlists(Playlist_Id,
                                            Playlist_Name ,
                                            Channel_Id, 
                                            Channel_Name ,
                                            PublishedAt,
                                            VideoCount 
                                            )
                                            VALUES(%s,%s,%s,%s,%s,%s)'''            
        values =(
                row['Playlist_ID'],
                row['Title'],
                row['ChannelId'],
                row['ChannelName'],
                row['PublishedAt'],
                row['VideoCount'])
                
        try:                     
            mycursor.execute(insert_query,values)
            mydb.commit()    
        except:
            st.write("Playlists values are inserted already")


#creating a table for comments
def comments_table():
    drop='''drop table if exists comments'''
    mycursor.execute(drop)
    mydb.commit()

    try:
        create_query = '''CREATE TABLE if not exists comments(Comment_Id varchar(255) primary key,
        Video_Id varchar(255),
        Comment_Text text, 
        Comment_Author varchar(255),
        Comment_Published DATETIME)'''
        mycursor.execute(create_query)
        mydb.commit()
        
    except:
        st.write("Commentsp Table already created")

    com_list = []
    db = client["Youtube_data"]
    coll1 = db["Channel Details"]
    for com_data in coll1.find({},{"_id":0,"comment_information":1}):
        for i in range(len(com_data["comment_information"])):
            com_list.append(com_data["comment_information"][i])
    df3 = pd.DataFrame(com_list)


    for index, row in df3.iterrows():
            insert_query = '''INSERT INTO comments (Comment_Id,
            Video_Id, 
            Comment_Text,
            Comment_Author,
            Comment_Published)
            VALUES (%s, %s, %s, %s, %s)

            '''
            values = (
                row['Comment_ID'],
                row['Video_ID'],
                row['Comment_text'],
                row['Comment_Author'],
                row['Comment_Published_Date']
            )
            try:
                mycursor.execute(insert_query,values)
                mydb.commit()
            except:
                st.write("This comments are already exist in comments table")
                

#creating a table for Videos
def videos_table():    
    drop='''drop table if exists videos'''
    mycursor.execute(drop)
    mydb.commit()

    try:
        create_query = '''create table if not exists videos(
                        Channel_Name varchar(255),
                        Channel_Id varchar(255),
                        Video_Id varchar(255) primary key, 
                        Title varchar(255), 
                        Tags text,
                        Thumbnail varchar(225),
                        Description text, 
                        Published_Date DATETIME,
                        Duration int, 
                        Views int, 
                        Likes int,
                        Comments int,
                        Favorite_Count int, 
                        Definition varchar(255), 
                        Caption_Status varchar(255) 
                        )''' 
                        
        mycursor.execute(create_query)             
        mydb.commit()
    except:
        st.write("Videos Table is created already")

    vi_list = []
    db = client["Youtube_data"]
    col1 = db["Channel Details"]
    for vi_data in col1.find({},{"_id":0,"video_information":1}):
        for i in range(len(vi_data["video_information"])):
            vi_list.append(vi_data["video_information"][i])
    df2 = pd.DataFrame(vi_list)
        
    
    for index, row in df2.iterrows():
        insert_query = '''
                    INSERT INTO videos (Channel_Name,
                        Channel_Id,
                        Video_Id, 
                        Title, 
                        Tags,
                        Thumbnail,
                        Description, 
                        Published_Date,
                        Duration, 
                        Views, 
                        Likes,
                        Comments,
                        Favorite_Count, 
                        Definition, 
                        Caption_Status
                        )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)

                '''
        values = (
                    row['Channel_name'],
                    row['Channel_id'],
                    row['Video_id'],
                    row['Video_name'],
                    row['Tags'],
                    row['Thumbnail'],
                    row['Description'],
                    row['Published_Date'],
                    row['Duration'],
                    row['Views'],
                    row['Likes'],
                    row['Comments'],
                    row['Favorite_count'],
                    row['Definition'],
                    row['Caption_status'])
                                
        try:    
            mycursor.execute(insert_query,values)
            mydb.commit()
        except:
            st.write("videos values already are inserted")
            

# Function Block that consists of four other functions to create tables such as channels,playlists,videos and comments
def tables():
    channels_table()
    playlists_table()
    videos_table()
    comments_table()
    return "Tables Created Successfully"


def show_channels_table():
    ch_list = []
    db = client["Youtube_data"]
    coll1 = db["Channel Details"] 
    for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
        ch_list.append(ch_data["channel_information"])
    channels_table = st.dataframe(ch_list)
    return channels_table

def show_playlists_table():
    db = client["Youtube_data"]
    coll1 =db["Channel Details"]
    pl_list = []
    for pl_data in coll1.find({},{"_id":0,"playlist_information":1}):
        for i in range(len(pl_data["playlist_information"])):
                pl_list.append(pl_data["playlist_information"][i])
    playlists_table = st.dataframe(pl_list)
    return playlists_table

def show_videos_table():
    vi_list = []
    db = client["Youtube_data"]
    coll2 = db["Channel Details"]
    for vi_data in coll2.find({},{"_id":0,"video_information":1}):
        for i in range(len(vi_data["video_information"])):
            vi_list.append(vi_data["video_information"][i])
    videos_table = st.dataframe(vi_list)
    return videos_table

def show_comments_table():
    com_list = []
    db = client["Youtube_data"]
    coll3 = db["Channel Details"]
    for com_data in coll3.find({},{"_id":0,"comment_information":1}):
        for i in range(len(com_data["comment_information"])):
            com_list.append(com_data["comment_information"][i])
    comments_table = st.dataframe(com_list)
    return comments_table

#building a streamlit application
with st.sidebar:
    st.title(":red[YOUTUBE DATA HARVESTING AND WAREHOUSING]")
    st.divider()
    st.caption(":black[Effortlessly explore and analyze data from multiple channels, dive into the metrics that matter most to you, and experience the re-imagined world of YouTube analytics]:rocket:")
    
channel_id = st.text_input("Channel ID")
channels = channel_id.split(',')
channels = [ch.strip() for ch in channels if ch]


if st.button("Collect Data",type="primary"):
    for channel in channels:
        ch_ids = []
        db = client["Youtube_data"]
        col1 = db["Channel Details"]
        for ch_data in col1.find({},{"_id":0,"channel_information":1}):
            ch_ids.append(ch_data["channel_information"]["Channel_id"])
        if channel in ch_ids:
            st.success("Channel details of the given channel id: " + channel + " already exists")
        else:
            output = channel_details(channel)
            st.success(output)
            
if st.button("Migrate Data to SQL",type="primary"):
    display = tables()
    st.success(display)
    
show_table = st.radio("SELECT THE TABLE BELOW TO VIEW",(":black[Channels]",":black[Playlists]",":black[Videos]",":black[Comments]"))

if show_table == ":black[Channels]":
    show_channels_table()
elif show_table == ":black[Playlists]":
    show_playlists_table()
elif show_table ==":black[Videos]":
    show_videos_table()
elif show_table == ":black[Comments]":
    show_comments_table()


question = st.selectbox('Curated Inquiries',
                        ('Please Select Your Question',
                        '1. Video and Channel Names Overview',
                        '2. Top Video Producers',
                        '3. Top 10 Most Viewed Videos',
                        '4. Comments Breakdown',
                        '5. Likes Leaderboard',
                        '6. Likes and Dislikes Analysis',
                        '7. Channel View Totals',
                        '8. 2022 Channel Publishers',
                        '9. Average Video Duration by Channel',
                        '10. Comment Champions'))

if question == '1. Video and Channel Names Overview':
    query1 = "select Title as videos, Channel_Name as ChannelName from videos;"
    mycursor.execute(query1)
    mydb.commit()
    t1=cursor.fetchall()
    st.write(pd.DataFrame(t1, columns=["Video Title","Channel Name"]))

elif question == '2. Top Video Producers':
    query2 = "select Channel_Name as ChannelName,Total_Videos as NO_Videos from channels order by Total_Videos desc;"
    mycursor.execute(query2)
    mydb.commit()
    t2=mycursor.fetchall()
    st.write(pd.DataFrame(t2, columns=["Channel Name","No Of Videos"]))

elif question == '3. Top 10 Most Viewed Videos':
    query3 = '''select Views as views , Channel_Name as ChannelName,Title as VideoTitle from videos 
                        where Views is not null order by Views desc limit 10;'''
    mycursor.execute(query3)
    mydb.commit()
    t3 = mycursor.fetchall()
    st.write(pd.DataFrame(t3, columns = ["views","channel Name","video title"]))

elif question == '4. Comments Breakdown':
    query4 = "select Comments as No_comments ,Title as VideoTitle from videos where Comments is not null;"
    mycursor.execute(query4)
    mydb.commit()
    t4=mycursor.fetchall()
    st.write(pd.DataFrame(t4, columns=["No Of Comments", "Video Title"]))

elif question == '5. Likes Leaderboard':
    query5 = '''select Title as VideoTitle, Channel_Name as ChannelName, Likes as LikesCount from videos 
    where Likes is not null order by Likes desc;'''
    mycursor.execute(query5)
    mydb.commit()
    t5 = mycursor.fetchall()
    st.write(pd.DataFrame(t5, columns=["video Title","channel Name","like count"]))

elif question == '6. Likes and Dislikes Analysis':
    query6 = '''select Likes as likeCount,Title as VideoTitle from videos;'''
    mycursor.execute(query6)
    mydb.commit()
    t6 = mycursor.fetchall()
    st.write(pd.DataFrame(t6, columns=["like count","video title"]))

elif question == '7. Channel View Totals':
    query7 = "select Channel_Name as ChannelName, Views as Channelviews from channels;"
    mycursor.execute(query7)
    mydb.commit()
    t7=mycursor.fetchall()
    st.write(pd.DataFrame(t7, columns=["channel name","total views"]))

elif question == '8. 2022 Channel Publishers':
    query8 = '''select Title as Video_Title, Published_Date as VideoRelease, Channel_Name as ChannelName from videos 
                where extract(year from Published_Date) = 2022;'''
    mycursor.execute(query8)
    mydb.commit()
    t8=mycursor.fetchall()
    st.write(pd.DataFrame(t8,columns=["Name", "Video Publised On", "ChannelName"]))

elif question == '9.Average Video Duration by Channel':
    query9 =  "SELECT Channel_Name as ChannelName, AVG(Duration) AS average_duration FROM videos GROUP BY Channel_Name;"
    mycursor.execute(query9)
    mydb.commit()
    t9=mycursor.fetchall()
    t9 = pd.DataFrame(t9, columns=['ChannelTitle', 'Average Duration'])
    T9=[]
    for index, row in t9.iterrows():
        channel_title = row['ChannelTitle']
        average_duration = row['Average Duration']
        average_duration_str = str(average_duration)
        T9.append({"Channel Title": channel_title ,  "Average Duration": average_duration_str})
    st.write(pd.DataFrame(T9))

elif question == '10. Comment Champions':
    query10 = '''select Title as VideoTitle, Channel_Name as ChannelName, Comments as Comments from videos 
    where Comments is not null order by Comments desc;'''
    mycursor.execute(query10)
    mydb.commit()
    t10=mycursor.fetchall()
    st.write(pd.DataFrame(t10, columns=['Video Title', 'Channel Name', 'NO Of Comments']))
