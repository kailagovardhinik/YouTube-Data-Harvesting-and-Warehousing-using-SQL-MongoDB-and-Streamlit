from googleapiclient.discovery import build
import streamlit as st 
import pandas as pd
import numpy as np
import json
import re
#creating a function for connection
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
def video_info(channel_id):
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
