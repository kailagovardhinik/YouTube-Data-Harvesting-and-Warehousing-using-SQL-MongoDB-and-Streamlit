from googleapiclient.discovery import build
import mysql.connector
import streamlit as st 
import pandas as pd
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
def channel_information(input_id):
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
def all_video_info(channel_id):
    Video_id_list=[]
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
            Video_id_list.append(request["items"][i]['snippet']['resourceId']['videoId'])
        next_page_tokens=request.get('nextPageToken')
        
        if next_page_tokens is None:
            break
    return Video_id_list

#creating a function to get information about video
def get_video_info(ids):
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
def get_comment_info(ids):
