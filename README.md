# YouTube Data Harvesting and Warehousing using SQL, MongoDB and Streamlit
<p align="left"> <a href="https://www.linkedin.com/in/kailagovardhinik/" target="_blank" rel="noreferrer"> <picture> <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/danielcranney/readme-generator/main/public/icons/socials/linkedin-dark.svg" /> <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/danielcranney/readme-generator/main/public/icons/socials/linkedin.svg" /> <img src="https://raw.githubusercontent.com/danielcranney/readme-generator/main/public/icons/socials/linkedin.svg" width="32" height="32" /> </picture> </a></p>

The primary aim of this project is to create an application to simplify the process of accessing and analyzing data from numerous YouTube channels. Users can input a specific YouTube channel ID to extract a range of data, such as the channel name, subscriber count, total video count, playlist ID, video ID, as well as metrics like likes, dislikes, and comments for each video. The Google API is utilized for this data retrieval process. Additionally, the data can be initially stored in a MongoDB database, serving as a data lake, before being transferred to a SQL database for more extensive analysis.
  
## Technologies Used

- Streamlit: A powerful tool for building data visualization and analysis apps quickly.
- Google API: Used for retrieving data from YouTube channels.
- MongoDB: Used as a data lake for storing raw data.
- SQL Database: Utilized for storing structured data for further analysis.

## Install Dependencies
- streamlit
- pandas
- pymongo
- googleapiclient.discovery
- 
## Set Up API Keys:
- Obtain YouTube API keys and MongoDB credentials. Update the config.py file with the necessary information.
- 
### Features
- Retrieve data for a YouTube channel (Channel name, subscribers, total video count, playlist ID, video ID, likes, dislikes, comments of each video) using Google API.
- Store data in a MongoDB database as a data lake.
- Collect data for up to 10 different YouTube channels and store them in the data lake.
- Migrate data from the data lake to a SQL database.
- Search and retrieve data from the SQL database with different search options, including joining tables.

### Approach
1. **Set up a Streamlit app:** Create a simple UI for user interaction.
2. **Connect to the YouTube API:** Use the Google API client library for Python.
3. **Store data in MongoDB:** Utilize MongoDB for its flexibility with unstructured data.
4. **Migrate data to SQL:** Transfer data to a SQL data warehouse (e.g., MySQL or PostgreSQL).
5. **Query the SQL data warehouse:** Use SQL queries, potentially with SQLAlchemy for interaction.
6. **Display data in Streamlit:** Leverage Streamlit's data visualization features for a user-friendly interface.

## SQL Query Outputs in Streamlit Application

1. What are the names of all the videos and their corresponding channels?
2. Which channels have the most number of videos, and how many videos do they have?
3. What are the top 10 most viewed videos and their respective channels?
4. How many comments were made on each video, and what are their corresponding video names?
5. Which videos have the highest number of likes, and what are their corresponding channel names?
6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?
7. What is the total number of views for each channel, and what are their corresponding channel names?
8. What are the names of all the channels that have published videos in the year 2022?
9. What is the average duration of all videos in each channel, and what are their corresponding channel names?
10. Which videos have the highest number of comments, and what are their corresponding channel names?


![image](https://github.com/kailagovardhinik/YouTube-Data-Harvesting-and-Warehousing-using-SQL-MongoDB-and-Streamlit/assets/141433548/c6031775-b685-4098-98e9-4603033fe4c0)


Feel free to contribute to this project by creating pull requests or raising issues.
