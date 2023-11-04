from googleapiclient.discovery import build
import mysql.connector
import streamlit as st 
import pandas as pd
import pymongo
import numpy as np
import json
import re
#creating a function for API connection
def Api_connect():
    api_key="AIzaSyDj5WwmFp4Qu03Px3qKzU0o0KsdrV_IJsw"
    api_service_name="youtube"
    api_version="v3"
    youtube = build(api_service_name,api_version, developerKey=api_key)
    return youtube
youtube=Api_connect()

#creating a function to get channel information
def channel_information(Channel_id):
    request = youtube.channels().list(
        part="snippet,statistics,contentDetails",
        id=input_id
    )
    response = request.execute()
    for i in response['items']:
        data = dict(Channel_Name=i["snippet"]["title"],
                    Channel_id=i["id"],
                    Subscriber=i["statistics"]["subscriberCount"],
                    Views=i["statistics"]['viewCount'],
                    Total_Videos=i["statistics"]['videoCount'],
                    Channel_Description=i["snippet"]['description'],
                    Playlist_id=i['contentDetails']['relatedPlaylists']['uploads'])
    return data
#creating a function to get information about all the videos of the channel 
def all_video_info(Channel_id):
    Video_id=[]
    response=youtube.channels().list(id=channel_id,
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

#creating a function to get information about video
def get_video_info(Video_id):
        video_data=[]
        for video_id in ids:
                request=youtube.videos().list(
                        part="snippet,contentDetails,statistics",
                        id=video_id
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
def get_comment_info(Video_id):
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
#connecting to Mongo DB
client=pymongo.MongoClient("mongodb://localhost:27017")
db=client["YouTube_Data"]

#uploading the data to MongoDB
def get_channel_details(Channel_ID):
    Channel_Detail=channel_information(Channel_ID)
    Playlist_Detail=get_playlist_details(Channel_ID)
    Video_Ids=all_video_info(Channel_ID)
    Video_info=get_video_information(Video_Ids)
    Comment_details=comment_information(Video_Ids)
  
    coll1=db["Channel Details"]
    coll1.insert_one({"channel_information":Channel_Detail,"playlist_information":Playlist_Detail,
                        "video_information":Video_Ids,"comment_information":Comment_details})
    return "Upload Complete Successfully"

#connecting to SQL
import mysql.connector
mydb=mysql.connector.connect(
    host="localhost",
    user="root",
    password="risehigh07",
    database="youtube_data",
    )
mycursor=mydb.cursor()

#creating a table for channels
try:
    create_query='''create table if not exists channels(channel_id varchar(255),
channel_name varchar(255),
channel_type varchar(255),
channel_views int,
channel_description text,
channel_status varchar(255)
    )'''
    mycursor.execute(create_query)
    mydb.commit()
except:
    print("Channel table created")
