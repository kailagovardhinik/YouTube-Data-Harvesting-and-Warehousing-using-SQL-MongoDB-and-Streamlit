from googleapiclient.discovery import build
import streamlit as st 
import pandas as pd
import numpy as np
import json
import re

api_key="AIzaSyDj5WwmFp4Qu03Px3qKzU0o0KsdrV_IJsw"
youtube = build('youtube', 'v3', developerKey=api_key)
channel_id="UCxwitsUVNzwS5XBSC5UQV8Q"
# selected **channel** from resource menu

response = youtube.channels().list(
    id=channel_id,
    part='snippet,statistics,contentDetails'
)

channel_data = response.execute()
