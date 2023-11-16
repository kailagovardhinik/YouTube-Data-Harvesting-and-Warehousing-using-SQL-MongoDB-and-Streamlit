from googleapiclient.discovery import build
import pymongo
from pymongo import MongoClient
import mysql.connector
import pandas as pd
import streamlit as st

#connecting to youtube using API Key
def Api_connect():
    api_key="AIzaSyDj5WwmFp4Qu03Px3qKzU0o0KsdrV_IJsw"
    
    youtube = build("youtube","v3", developerKey=api_key)
    
    return youtube

youtube=Api_connect()
#creating a function to get channel information when a channel Id is provided
def channel_information(Channel_id):
    request = youtube.channels().list(
        part="snippet,statistics,contentDetails",
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
                    Playlist_id=i['contentDetails']['relatedPlaylists']['uploads'])
    return data

#creating a function to get information about all the video id of the channel 
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

#creating a function to get information about each video
def get_video_information(Video_id):
        video_data=[]
        for video_ids in Video_id:
                request=youtube.videos().list(
                        part="snippet,contentDetails,statistics",
                        id=video_ids
                )
                response=request.execute()
                for item in response['items']:
                        data=dict(Channel_name=item["snippet"]['channelTitle'],
                                Channel_id=item["snippet"]['channelId'],
                                Video_id=item['id'],
                                Title=item['snippet']["title"],
                                Tags=item.get('tags'),
                                Thumbnail=item['snippet']['thumbnails'],
                                Description=item.get('description'),
                                Published_Date=item['snippet']['publishedAt'],
                                Duration=item['contentDetails']['duration'],
                                Views=item.get('viewCount'),
                                Comments=item.get('commentCount'),
                                Favorite_count=item['statistics']['favoriteCount'],
                                Definition=item['contentDetails']['definition'],
                                Caption_status=item['contentDetails']['caption']
                                )
                        video_data.append(data)
        return video_data
    
#creating a function to get comment information
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
                    Title=item['snippet']['title'],
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

client=pymongo.MongoClient("mongodb://localhost:27017")
db=client["YouTube_Data"]

def channel_details(Channel_ID):
    Channel_Detail=channel_information(Channel_ID)
    Playlist_Detail=get_playlist_details(Channel_ID)
    Video_Ids=all_video_info(Channel_ID)
    Video_info=get_video_information(Video_Ids)
    Comment_details=comment_information(Video_Ids)

    coll1=db["Channel Details"]
    coll1.insert_one({"channel_information":Channel_Detail,"playlist_information":Playlist_Detail,
                        "video_information":Video_Ids,"comment_information":Comment_details})
    return "Upload Complete Successfully"

#creating a table for channels 
def channels_table():
    mydb=mysql.connector.connect(
        host="localhost",
        user="root",
        password="risehigh07",
        database="youtube_data"
        )
    mycursor=mydb.cursor()
    drop='''drop table if exists channels'''
    mycursor.execute(drop)
    mydb.commit()

    #creating a table for channels
    try:
        create_query='''create table if not exists channels(Channel_name varchar(255),
    Channel_ID varchar(255),
    Subscribers int,
    Channel_views int,
    Total_videos int,
    Channel_description text,
    Playlist_ID varchar(255)
        )'''
        mycursor.execute(create_query)
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
        insert='''insert into channels(Channel_name,
                                    Channel_ID,
                                    Subscribers,
                                    Channel_views,
                                    Total_videos,
                                    Channel_description,
                                    Playlist_ID)
                                    
                                    values(%s,%s,%s,%s,%s,%s,%s)'''  

        values=(row['Channel_Name'],
                row["Channel_id"],
                row["Subscription_counts"],
                row["Channel_Views"],
                row["Total_Videos"],
                row["Channel_Description"],
                row["Playlist_id"])
        try:
            mycursor.execute(insert,values)
            mydb.commit()
        except:
            st.write("Channel values are inserted already")

#creating a table for playlist 
def playlists_table():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="risehigh07",
        database="youtube_data"
        )
    mycursor=mydb.cursor()
    drop='''drop table if exists playlists'''
    mycursor.execute(drop)
    mydb.commit()

    try:
        create_query = '''create table if not exists playlists(PlaylistId varchar(100) primary key,
                        Title varchar(80), 
                        ChannelId varchar(100), 
                        ChannelName varchar(100),
                        PublishedAt timestamp,
                        VideoCount int
                        )
                        '''
        mycursor.execute(create_query)
        mydb.commit()
    except:
        st.write("Playlists Table is created already")    


    db = client["Youtube_data"]
    coll1 =db["Channel Details"]
    pl_list = []
    for pl_data in coll1.find({},{"_id":0,"playlist_information":1}):
        for i in range(len(pl_data["playlist_information"])):
                pl_list.append(pl_data["playlist_information"][i])
    df = pd.DataFrame(pl_list)
    
    for index,row in df.iterrows():
        insert_query = '''INSERT into playlists(PlaylistId,
                                                    Title,
                                                    ChannelId,
                                                    ChannelName,
                                                    PublishedAt,
                                                    VideoCount)
                                        VALUES(%s,%s,%s,%s,%s,%s)'''            
        values =(
                row['PlaylistId'],
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

#creating a table for Videos

def videos_table():    
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="risehigh07",
        database="youtube_data"
        )
    mycursor=mydb.cursor()
    drop='''drop table if exists videos'''
    mycursor.execute(drop)
    mydb.commit()

    try:
        create_query = '''create table if not exists videos(
                        Channel_Name varchar(150),
                        Channel_Id varchar(100),
                        Video_Id varchar(50) primary key, 
                        Title varchar(150), 
                        Tags text,
                        Thumbnail varchar(225),
                        Description text, 
                        Published_Date timestamp,
                        Duration interval, 
                        Views bigint, 
                        Likes bigint,
                        Comments int,
                        Favorite_Count int, 
                        Definition varchar(10), 
                        Caption_Status varchar(50) 
                        )''' 
                        
        mycursor.execute(create_query)             
        mydb.commit()
    except:
        st.write("Videos Table is created already")

    vi_list = []
    db = client["Youtube_data"]
    coll1 = db["Channel Details"]
    for vi_data in coll1.find({},{"_id":0,"video_information":1}):
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
                    row['Channel_Name'],
                    row['Channel_Id'],
                    row['Video_Id'],
                    row['Title'],
                    row['Tags'],
                    row['Thumbnail'],
                    row['Description'],
                    row['Published_Date'],
                    row['Duration'],
                    row['Views'],
                    row['Likes'],
                    row['Comments'],
                    row['Favorite_Count'],
                    row['Definition'],
                    row['Caption_Status'])
                                
        try:    
            mycursor.execute(insert_query,values)
            mydb.commit()
        except:
            st.write("videos values already are inserted")

#creating a table for comments
def comments_table():
    
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="risehigh07",
        database="youtube_data"
        )
    mycursor=mydb.cursor()
    drop='''drop table if exists comments'''
    mycursor.execute(drop)
    mydb.commit()

    try:
        create_query = '''CREATE TABLE if not exists comments(Comment_Id varchar(100) primary key,
        Video_Id varchar(80),
        Comment_Text text, 
        Comment_Author varchar(150),
        Comment_Published timestamp)'''
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
                row['Comment_Id'],
                row['Video_Id'],
                row['Comment_Text'],
                row['Comment_Author'],
                row['Comment_Published']
            )
            try:
                mycursor.execute(insert_query,values)
                mydb.commit()
            except:
                st.write("This comments are already exist in comments table") 
                
                

def tables():
    channels_table()
    playlists_table()
    videos_table()
    comments_table()
    return "Tables Created successfully"
    
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
    
channel_id = st.text_input("Channel ID")
channels = channel_id.split(',')
channels = [ch.strip() for ch in channels if ch]

if st.button("Collect and Store Data"):
    for channel in channels:
        ch_ids = []
        db = client["Youtube_data"]
        coll1 = db["Channel Details"]
        for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
            ch_ids.append(ch_data["channel_information"]["Channel_id"])
        if channel in ch_ids:
            st.success("Channel details of the given channel id: " + channel + " already exists")
        else:
            output = channel_details(channel)
            st.success(output)
            
if st.button("Migrate Data to SQL"):
    display = tables()
    st.success(display)
    
show_table = st.radio("SELECT THE TABLE FOR VIEW",(":black[Channels]",":black[Playlists]",":black[Videos]",":black[Comments]"))

if show_table == ":black[Channels]":
    show_channels_table()
elif show_table == ":black[Playlists]":
    show_playlists_table()
elif show_table ==":black[Videos]":
    show_videos_table()
elif show_table == ":black[Comments]":
    show_comments_table()

#SQL connection
mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="risehigh07",
        database="youtube_data"
        )
mycursor = mydb.cursor()
    
question = st.selectbox('Curated Inquiries',
    ('Please Select Your Question',
    '1. All the videos and channel Name',
    '2. Channels with most number of videos',
    '3. 10 most viewed videos',
    '4. Comments in each video',
    '5. Videos with highest likes',
    '6. likes of all videos',
    '7. views of each channel',
    '8. videos published in the year 2022',
    '9. average duration of all videos in each channel',
    '10. videos with highest number of comments'))

if question == '1. All the videos and the channel Name':
    query1 = "select Title as videos, Channel_Name as ChannelName from videos;"
    mycursor.execute(query1)
    mydb.commit()
    t1=cursor.fetchall()
    st.write(pd.DataFrame(t1, columns=["Video Title","Channel Name"]))
elif question == '2. Channels with most number of videos':
    query2 = "select Channel_Name as ChannelName,Total_Videos as NO_Videos from channels order by Total_Videos desc;"
    mycursor.execute(query2)
    mydb.commit()
    t2=mycursor.fetchall()
    st.write(pd.DataFrame(t2, columns=["Channel Name","No Of Videos"]))

elif question == '3. 10 most viewed videos':
    query3 = '''select Views as views , Channel_Name as ChannelName,Title as VideoTitle from videos 
                        where Views is not null order by Views desc limit 10;'''
    mycursor.execute(query3)
    mydb.commit()
    t3 = mycursor.fetchall()
    st.write(pd.DataFrame(t3, columns = ["views","channel Name","video title"]))

elif question == '4. Comments in each video':
    query4 = "select Comments as No_comments ,Title as VideoTitle from videos where Comments is not null;"
    mycursor.execute(query4)
    mydb.commit()
    t4=mycursor.fetchall()
    st.write(pd.DataFrame(t4, columns=["No Of Comments", "Video Title"]))

elif question == '5. Videos with highest likes':
    query5 = '''select Title as VideoTitle, Channel_Name as ChannelName, Likes as LikesCount from videos 
    where Likes is not null order by Likes desc;'''
    mycursor.execute(query5)
    mydb.commit()
    t5 = mycursor.fetchall()
    st.write(pd.DataFrame(t5, columns=["video Title","channel Name","like count"]))

elif question == '6. likes of all videos':
    query6 = '''select Likes as likeCount,Title as VideoTitle from videos;'''
    mycursor.execute(query6)
    mydb.commit()
    t6 = mycursor.fetchall()
    st.write(pd.DataFrame(t6, columns=["like count","video title"]))

elif question == '7. views of each channel':
    query7 = "select Channel_Name as ChannelName, Views as Channelviews from channels;"
    mycursor.execute(query7)
    mydb.commit()
    t7=mycursor.fetchall()
    st.write(pd.DataFrame(t7, columns=["channel name","total views"]))

elif question == '8. videos published in the year 2022':
    query8 = '''select Title as Video_Title, Published_Date as VideoRelease, Channel_Name as ChannelName from videos 
                where extract(year from Published_Date) = 2022;'''
    mycursor.execute(query8)
    mydb.commit()
    t8=mycursor.fetchall()
    st.write(pd.DataFrame(t8,columns=["Name", "Video Publised On", "ChannelName"]))

elif question == '9. average duration of all videos in each channel':
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

elif question == '10. videos with highest number of comments':
    query10 = '''select Title as VideoTitle, Channel_Name as ChannelName, Comments as Comments from videos 
    where Comments is not null order by Comments desc;'''
    mycursor.execute(query10)
    mydb.commit()
    t10=mycursor.fetchall()
    st.write(pd.DataFrame(t10, columns=['Video Title', 'Channel Name', 'NO Of Comments']))
