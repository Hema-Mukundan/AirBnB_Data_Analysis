# AirBnB_Data_Analysis
# Problem Statement:
This project aims to analyze Airbnb data using MongoDB Atlas, perform data cleaning and preparation, develop interactive geospatial visualizations, and create dynamic plots to gain insights into pricing variations, availability patterns, and location-based trends. The objectives are to:

1. Establish a MongoDB connection, retrieve the Airbnb dataset, and ensure efficient data retrieval for analysis.
2. Clean and prepare the dataset, addressing missing values, duplicates, and data type conversions for accurate analysis.
3. Develop a streamlit web application with interactive maps showcasing the distribution of Airbnb listings, allowing users to explore prices, ratings, and other relevant factors.
4. Conduct price analysis and visualization, exploring variations based on location, property type, and seasons using dynamic plots and charts.
5. Analyze availability patterns across seasons, visualizing occupancy rates and demand fluctuations using suitable visualizations.
6. Investigate location-based insights by extracting and visualizing data for specific regions or neighborhoods.
7. Create interactive visualizations that enable users to filter and drill down into the data.
8. Build a comprehensive dashboard using Tableau or Power BI, combining various visualizations to present key insights from the analysis.

# Data: MongoDb - Atlas

# Steps followed
1. Create a MongoDB Atlas Account: Sign up for a MongoDB Atlas account by visiting the MongoDB Atlas website and follow the registration process to set up your account and create a new project.
2. Set Up a Cluster: Within your MongoDB Atlas project, set up a cluster. Choose the cloud provider and region for hosting your data, configure the cluster specifications, and create the cluster. This will serve as the database environment for storing the sample data.
3. Load the Airbnb Sample Data: Once your cluster is set up, access the MongoDB Atlas dashboard. In the left-hand navigation menu, click on "Database Access" to create a database user with appropriate permissions for accessing and loading data. Then, select "Network Access" to set up IP whitelisting or configure other security measures.
4. Import Sample Data: From the MongoDB Atlas dashboard, navigate to the "Clusters" page and click on your cluster. In the cluster view, select the "Collections" tab and click on the "Sample Data" button. Choose the "Load Sample Dataset" option, and MongoDB Atlas will import the Airbnb sample data into your cluster. The sample data typically includes collections for listings, reviews, and users.
