# YouTube Data Harvesting and Warehousing using SQL, MongoDB and Streamlit
The primary aim of this project is to create an application to simplify the process of accessing and analyzing data from numerous YouTube channels. Users can input a specific YouTube channel ID to extract a range of data, such as the channel name, subscriber count, total video count, playlist ID, video ID, as well as metrics like likes, dislikes, and comments for each video. The Google API is utilized for this data retrieval process. Additionally, the data can be initially stored in a MongoDB database, serving as a data lake, before being transferred to a SQL database for more extensive analysis.

## Features

- Input a YouTube channel ID to retrieve various data points from the YouTube API.
- Store retrieved data in a MongoDB database as a data lake.
- Collect data for up to 10 different YouTube channels and store them in the data lake by clicking a button.
- Select a channel name and migrate its data from the data lake to a SQL database as tables.
- Search and retrieve data from the SQL database using different search options, including joining tables to get channel details.
- Display the retrieved data in the Streamlit app for easy visualization and analysis.
  
## Technologies Used

- Streamlit: A powerful tool for building data visualization and analysis apps quickly.
- Google API: Used for retrieving data from YouTube channels.
- MongoDB: Used as a data lake for storing raw data.
- SQL Database: Utilized for storing structured data for further analysis.

Feel free to contribute to this project by creating pull requests or raising issues.

##Project Workflow
- User inputs YouTube channel ID in the Streamlit app.
- Data is retrieved from the YouTube API.
- Retrieved data is stored in MongoDB as a data lake.
- User clicks a button to collect data for up to 10 different YouTube channels and stores them in the data lake.
- User selects a channel name to migrate its data from the data lake to a SQL database as tables.
- User queries the SQL database using different search options in the Streamlit app.
- SQL query results are displayed as tables in the Streamlit app.
