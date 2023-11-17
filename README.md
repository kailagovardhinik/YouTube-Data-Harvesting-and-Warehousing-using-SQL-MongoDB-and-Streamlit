# YouTube Data Harvesting and Warehousing using SQL, MongoDB and Streamlit
The primary aim of this project is to create an application to simplify the process of accessing and analyzing data from numerous YouTube channels. Users can input a specific YouTube channel ID to extract a range of data, such as the channel name, subscriber count, total video count, playlist ID, video ID, as well as metrics like likes, dislikes, and comments for each video. The Google API is utilized for this data retrieval process. Additionally, the data can be initially stored in a MongoDB database, serving as a data lake, before being transferred to a SQL database for more extensive analysis.
  
## Technologies Used

- Streamlit: A powerful tool for building data visualization and analysis apps quickly.
- Google API: Used for retrieving data from YouTube channels.
- MongoDB: Used as a data lake for storing raw data.
- SQL Database: Utilized for storing structured data for further analysis.

## Libraries Used
- streamlit
- pandas
- pymongo
- googleapiclient.discovery

## Project Workflow:

1.  User Inputs YouTube Channel ID in the Streamlit app:
-	The user can manually input a YouTube channel ID for immediate data retrieval.
2.	Scheduled Data Collection and Storage:
-	Introduce a scheduling option in the Streamlit app where users can specify the frequency (daily, weekly, etc.) and time for automatic data collection for their selected YouTube channels.
-	Implement a background task that runs at the scheduled time to fetch the latest data from the YouTube API for the specified channels.
-	Store the retrieved data in MongoDB as part of the data lake.
3.	User Clicks a Button to Collect Data for Up to 10 Channels:
-	Users can still manually trigger the data collection process for immediate needs.
4.	User Selects a Channel Name to Migrate Data to SQL Database:
-	The user can choose a specific channel from the data lake for migration to the SQL database as tables.
5.	User Queries SQL Database in Streamlit App:
-	Enhance the SQL query options to include filtering based on the time of data collection or other relevant parameters.
-	Users can still join tables to get detailed information about the selected YouTube channels.
6.	Display Query Results in Streamlit App:
-	The Streamlit app should display the results of SQL queries in tables for easy visualization and analysis.
-	Provide options for exporting/query results for further analysis or sharing.

![pro 1](https://github.com/kailagovardhinik/YouTube-Data-Harvesting-and-Warehousing-using-SQL-MongoDB-and-Streamlit/assets/141433548/30cb14b9-fd06-46ab-ac81-6c83d157cfe4)


Feel free to contribute to this project by creating pull requests or raising issues.
